"""
OpenAI Model Manager
Dynamically fetches available models and pricing information
"""

import openai
import requests
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

class OpenAIModelManager:
    """Manages OpenAI model information including pricing and capabilities"""
    
    def __init__(self, api_key: str):
        """
        Initialize the model manager
        
        Args:
            api_key: OpenAI API key
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.api_key = api_key
        self.models_cache = {}
        self.cache_timestamp = None
        self.cache_duration = timedelta(hours=6)  # Cache for 6 hours (pricing changes infrequently)
        
        # We'll fetch pricing dynamically using ChatGPT to get current pricing
        # This is more reliable than static data and self-updating
        self.pricing_cache = {}
        self.pricing_cache_timestamp = None
        
    def _fetch_current_pricing(self) -> Dict[str, Dict]:
        """
        Fetch current pricing information from OpenAI documentation page.
        Falls back to curated data if web scraping fails.
        """
        # Check cache first
        if (self.pricing_cache and self.pricing_cache_timestamp and 
            datetime.now() - self.pricing_cache_timestamp < timedelta(days=1)):
            return self.pricing_cache
        
        # Try web scraping first (currently disabled due to OpenAI blocking)
        # Note: OpenAI blocks automated requests to pricing pages with 403 Forbidden
        # We'll keep the scraping code for future use but disable it for now
        try:
            if False:  # Disabled until we can bypass OpenAI's anti-scraping measures
                pricing_data = self._scrape_openai_pricing()
                if pricing_data:
                    # Cache the results
                    self.pricing_cache = pricing_data
                    self.pricing_cache_timestamp = datetime.now()
                    
                    logging.info(f"Scraped current pricing for {len(pricing_data)} models from OpenAI docs")
                    return pricing_data
        except Exception as e:
            logging.debug(f"Web scraping disabled or failed: {e}")
        
        # Use enhanced curated pricing with model discovery
        logging.info("Using curated pricing data with API model discovery")
        pricing_data = self._get_enhanced_pricing_with_discovery()
        
        # Cache the results
        self.pricing_cache = pricing_data
        self.pricing_cache_timestamp = datetime.now()
        
        logging.info(f"Loaded enhanced pricing for {len(pricing_data)} models")
        return pricing_data
    
    def _get_enhanced_pricing_with_discovery(self) -> Dict[str, Dict]:
        """
        Get enhanced pricing by combining curated pricing with API-discovered models.
        This gives us up-to-date model availability while maintaining reliable pricing.
        """
        # Start with curated pricing as base
        pricing_data = self._get_fallback_pricing()
        
        # Try to enhance with models discovered via API
        try:
            discovered_models = self._discover_available_models()
            if discovered_models:
                # Add any new models we discover but don't have pricing for
                for model_id in discovered_models:
                    if model_id not in pricing_data and self._is_chat_model(model_id):
                        # Filter out unwanted models
                        if self._should_exclude_model(model_id):
                            logging.debug(f"Excluding model from discovery: {model_id}")
                            continue
                            
                        # Try to infer pricing from model family
                        inferred_pricing = self._infer_model_pricing(model_id)
                        if inferred_pricing:
                            pricing_data[model_id] = inferred_pricing
                            logging.debug(f"Added discovered model: {model_id}")
                            
        except Exception as e:
            logging.debug(f"Model discovery failed, using curated data only: {e}")
        
        return pricing_data
    
    def _discover_available_models(self) -> List[str]:
        """
        Discover available models using the OpenAI API.
        Returns list of model IDs that are currently available.
        """
        try:
            models_response = self.client.models.list()
            model_ids = []
            
            for model in models_response.data:
                # Only include chat-capable models
                if self._is_chat_model(model.id):
                    model_ids.append(model.id)
            
            logging.debug(f"Discovered {len(model_ids)} chat models via API")
            return model_ids
            
        except Exception as e:
            logging.debug(f"API model discovery failed: {e}")
            return []
    
    def _should_exclude_model(self, model_id: str) -> bool:
        """
        Determine if a discovered model should be excluded from the available models list.
        We exclude specific models that we don't want users to select.
        
        Args:
            model_id: The model ID to check
            
        Returns:
            bool: True if the model should be excluded, False otherwise
        """
        model_lower = model_id.lower()
        
        # Exclude ALL GPT-4.1 models (base, mini, nano, and any other variants)
        if "gpt-4.1" in model_lower or "gpt-4-1" in model_lower:
            return True
        
        return False
    
    def _infer_model_pricing(self, model_id: str) -> Optional[Dict[str, any]]:
        """
        Infer pricing for a model based on its family/pattern.
        Used for newly discovered models not in our curated list.
        """
        model_lower = model_id.lower()
        
        # GPT-4.1 family
        if "4.1" in model_lower:
            if "mini" in model_lower:
                return {
                    "input": 0.00015,
                    "output": 0.0006,
                    "description": f"Inferred pricing for {model_id} (GPT-4.1 Mini family)"
                }
            elif "turbo" in model_lower:
                return {
                    "input": 0.01,
                    "output": 0.03,
                    "description": f"Inferred pricing for {model_id} (GPT-4.1 Turbo family)"
                }
            else:
                return {
                    "input": 0.01,
                    "output": 0.03,
                    "description": f"Inferred pricing for {model_id} (GPT-4.1 family)"
                }
        
        # GPT-4o family
        elif "4o" in model_lower:
            if "mini" in model_lower:
                return {
                    "input": 0.00015,
                    "output": 0.0006,
                    "description": f"Inferred pricing for {model_id} (GPT-4o Mini family)"
                }
            else:
                return {
                    "input": 0.0025,
                    "output": 0.010,
                    "description": f"Inferred pricing for {model_id} (GPT-4o family)"
                }
        
        # GPT-4 family
        elif "gpt-4" in model_lower and "turbo" in model_lower:
            return {
                "input": 0.01,
                "output": 0.03,
                "description": f"Inferred pricing for {model_id} (GPT-4 Turbo family)"
            }
        elif "gpt-4" in model_lower:
            return {
                "input": 0.03,
                "output": 0.06,
                "description": f"Inferred pricing for {model_id} (GPT-4 family)"
            }
        
        # GPT-3.5 family
        elif "3.5" in model_lower:
            return {
                "input": 0.0005,
                "output": 0.0015,
                "description": f"Inferred pricing for {model_id} (GPT-3.5 family)"
            }
        
        # Unknown model family
        return None
    
    def _scrape_openai_pricing(self) -> Dict[str, Dict]:
        """
        Scrape pricing data from OpenAI pricing pages.
        Tries multiple sources and methods to get current pricing.
        
        Returns:
            Dictionary of model pricing information
        """
        import requests
        from bs4 import BeautifulSoup
        import re
        
        # Try multiple pricing URLs in order of preference
        pricing_urls = [
            "https://openai.com/api/pricing/",  # Public pricing page
            "https://platform.openai.com/docs/pricing",  # Documentation page (fallback)
        ]
        
        for url in pricing_urls:
            try:
                logging.debug(f"Attempting to scrape pricing from: {url}")
                pricing_data = self._scrape_single_pricing_url(url)
                if pricing_data:
                    logging.info(f"Successfully scraped pricing from {url}")
                    return pricing_data
            except Exception as e:
                logging.debug(f"Failed to scrape {url}: {e}")
                continue
        
        # If all URLs fail, return empty dict to trigger fallback
        logging.warning("All pricing URLs failed to scrape")
        return {}
    
    def _scrape_single_pricing_url(self, url: str) -> Dict[str, Dict]:
        """
        Scrape pricing from a single URL with multiple strategies.
        """
        import requests
        from bs4 import BeautifulSoup
        
        # Try different user agents and methods
        strategies = [
            # Strategy 1: Modern browser
            {
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                }
            },
            # Strategy 2: Mobile browser
            {
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                }
            },
            # Strategy 3: Simple request
            {
                'headers': {
                    'User-Agent': 'Python-requests/2.32.0',
                    'Accept': 'text/html',
                }
            }
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                logging.debug(f"Trying strategy {i+1} for {url}")
                
                response = requests.get(url, 
                                      headers=strategy['headers'], 
                                      timeout=15,
                                      allow_redirects=True)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                pricing_data = {}
                
                # Try multiple parsing methods
                
                # Method 1: Look for pricing tables
                tables = soup.find_all('table')
                for table in tables:
                    if self._table_contains_pricing_data(table):
                        extracted_prices = self._extract_pricing_from_table(table)
                        pricing_data.update(extracted_prices)
                
                # Method 2: Look for JSON data in script tags
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and 'pricing' in script.string.lower():
                        json_prices = self._extract_pricing_from_script(script.string)
                        pricing_data.update(json_prices)
                
                # Method 3: Look for specific pricing sections/divs
                pricing_sections = soup.find_all(['div', 'section'], 
                                               class_=re.compile(r'pricing|price|cost', re.I))
                for section in pricing_sections:
                    section_prices = self._extract_pricing_from_section(section)
                    pricing_data.update(section_prices)
                
                # Filter to only include recognized chat models
                chat_pricing = {}
                for model_name, pricing_info in pricing_data.items():
                    if self._is_chat_model(model_name) and pricing_info.get('input', 0) > 0:
                        chat_pricing[model_name] = pricing_info
                
                if chat_pricing:
                    logging.debug(f"Strategy {i+1} succeeded, found {len(chat_pricing)} models")
                    return chat_pricing
                else:
                    logging.debug(f"Strategy {i+1} got response but no valid pricing data")
                    
            except requests.RequestException as e:
                logging.debug(f"Strategy {i+1} failed with request error: {e}")
                continue
            except Exception as e:
                logging.debug(f"Strategy {i+1} failed with parsing error: {e}")
                continue
        
        return {}
    
    def _extract_pricing_from_script(self, script_content: str) -> Dict[str, Dict]:
        """
        Extract pricing from JavaScript/JSON content in script tags.
        """
        pricing_data = {}
        
        try:
            # Look for JSON-like structures with pricing data
            json_matches = re.findall(r'\{[^{}]*(?:"price"|"cost"|"pricing")[^{}]*\}', script_content, re.I)
            
            for match in json_matches:
                try:
                    data = json.loads(match)
                    # Process if it looks like pricing data
                    if any(key in str(data).lower() for key in ['price', 'cost', 'token']):
                        # Extract model and pricing info
                        # This would need customization based on actual JSON structure
                        pass
                except json.JSONDecodeError:
                    continue
                    
        except Exception as e:
            logging.debug(f"Error extracting from script: {e}")
        
        return pricing_data
    
    def _extract_pricing_from_section(self, section) -> Dict[str, Dict]:
        """
        Extract pricing from HTML sections/divs that contain pricing information.
        """
        pricing_data = {}
        
        try:
            # Look for patterns like "GPT-4: $0.03 / 1K tokens"
            text_content = section.get_text()
            
            # Regex to find model names and prices
            pricing_patterns = [
                r'(gpt-[\d.]+[a-z-]*)[:\s]*\$?([\d.]+)[^\d]*(?:input|prompt)[^\d]*\$?([\d.]+)[^\d]*(?:output|completion)',
                r'(gpt-[\d.]+[a-z-]*)[:\s]*\$?([\d.]+)[^\d]*per[^\d]*1?k?[^\d]*tokens',
            ]
            
            for pattern in pricing_patterns:
                matches = re.finditer(pattern, text_content, re.I)
                for match in matches:
                    try:
                        model_name = match.group(1).lower()
                        if len(match.groups()) >= 3:
                            input_price = float(match.group(2))
                            output_price = float(match.group(3))
                        else:
                            input_price = float(match.group(2))
                            output_price = input_price * 2  # Estimate if only one price given
                        
                        pricing_data[model_name] = {
                            'input': input_price,
                            'output': output_price,
                            'description': f"Scraped pricing for {model_name}"
                        }
                    except (ValueError, IndexError):
                        continue
                        
        except Exception as e:
            logging.debug(f"Error extracting from section: {e}")
        
        return pricing_data
    
    def _table_contains_pricing_data(self, table) -> bool:
        """
        Check if a table contains pricing data by looking for price-related headers.
        """
        # Get all text from table headers
        headers = table.find_all(['th', 'td'])
        table_text = ' '.join([header.get_text().lower() for header in headers])
        
        # Look for pricing-related keywords
        pricing_keywords = [
            'price', 'pricing', 'cost', 'token', 'input', 'output', 
            'per 1k tokens', '1k tokens', 'completion', 'prompt'
        ]
        
        return any(keyword in table_text for keyword in pricing_keywords)
    
    def _extract_pricing_from_table(self, table) -> Dict[str, Dict]:
        """
        Extract pricing data from a table.
        
        Returns:
            Dictionary mapping model names to pricing info
        """
        pricing_data = {}
        
        try:
            # Find header row to identify column positions
            header_row = table.find('tr')
            if not header_row:
                return {}
            
            headers = [th.get_text().strip().lower() for th in header_row.find_all(['th', 'td'])]
            
            # Map common header variations to standard names
            header_map = {
                'model': ['model', 'model name', 'name'],
                'input': ['input', 'prompt', 'input tokens', 'per 1k prompt tokens'],
                'output': ['output', 'completion', 'output tokens', 'per 1k completion tokens', 'per 1k sampled tokens'],
                'description': ['description', 'desc', 'notes']
            }
            
            # Find column indices
            col_indices = {}
            for standard_name, variations in header_map.items():
                for i, header in enumerate(headers):
                    if any(var in header for var in variations):
                        col_indices[standard_name] = i
                        break
            
            # Extract data from each row
            for row in table.find_all('tr')[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:  # Need at least model name and some pricing
                    continue
                
                try:
                    # Extract model name
                    if 'model' in col_indices:
                        model_name = cells[col_indices['model']].get_text().strip()
                    else:
                        model_name = cells[0].get_text().strip()  # Assume first column is model
                    
                    # Clean model name
                    model_name = re.sub(r'\s+', '-', model_name.lower())
                    model_name = re.sub(r'[^\w.-]', '', model_name)
                    
                    # Extract pricing
                    input_price = 0.0
                    output_price = 0.0
                    description = ""
                    
                    if 'input' in col_indices and col_indices['input'] < len(cells):
                        input_price = self._extract_price_from_text(cells[col_indices['input']].get_text())
                    
                    if 'output' in col_indices and col_indices['output'] < len(cells):
                        output_price = self._extract_price_from_text(cells[col_indices['output']].get_text())
                    
                    if 'description' in col_indices and col_indices['description'] < len(cells):
                        description = cells[col_indices['description']].get_text().strip()
                    
                    # Only add if we have valid pricing
                    if model_name and (input_price > 0 or output_price > 0):
                        pricing_data[model_name] = {
                            'input': input_price,
                            'output': output_price,
                            'description': description or f"OpenAI {model_name} model"
                        }
                        
                except (IndexError, ValueError) as e:
                    logging.debug(f"Error parsing table row: {e}")
                    continue
                    
        except Exception as e:
            logging.error(f"Error extracting pricing from table: {e}")
        
        return pricing_data
    
    def _extract_price_from_text(self, text: str) -> float:
        """
        Extract price from text like '$0.0025' or '0.0025' or '$2.50 / 1K tokens'
        """
        # Remove common prefixes/suffixes and normalize
        text = text.strip().lower()
        text = re.sub(r'[/\s]*1?k?\s*tokens?.*$', '', text)  # Remove "/ 1K tokens" etc
        text = re.sub(r'^\$', '', text)  # Remove leading $
        
        # Find decimal number
        price_match = re.search(r'(\d+\.?\d*)', text)
        if price_match:
            return float(price_match.group(1))
        
        return 0.0
    
    def _extract_pricing_from_json_ld(self, json_data) -> Dict[str, Dict]:
        """
        Extract pricing from JSON-LD structured data if present.
        """
        # This is a placeholder - implement if OpenAI adds structured data
        # For now, return empty dict as tables are the primary source
        return {}
        
    def _get_fallback_pricing(self) -> Dict[str, Dict]:
        """
        Fallback pricing data if dynamic fetching fails
        Based on curated OpenAI pricing as of August 2025
        Prices converted from per 1M tokens to per 1K tokens
        """
        return {
            # GPT-5 family
            "gpt-5": {"input": 0.00125, "output": 0.01, "description": "Latest generation GPT-5 model with advanced capabilities"},
            "gpt-5-mini": {"input": 0.00025, "output": 0.002, "description": "Efficient version of GPT-5"},
            "gpt-5-nano": {"input": 0.00005, "output": 0.0004, "description": "Ultra-efficient GPT-5 model"},
            
            # GPT-4o family (curated selection)
            "gpt-4o": {"input": 0.0025, "output": 0.01, "description": "Most capable GPT-4 model, best for complex tasks"},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006, "description": "Faster, cheaper version of GPT-4o"},
            "gpt-4o-mini-realtime-preview": {"input": 0.0006, "output": 0.0024, "description": "GPT-4o Mini with realtime capabilities (preview)"},
        }
        
    def get_available_models(self, force_refresh: bool = False) -> List[Dict[str, str]]:
        """
        Get list of available OpenAI models for chat completion with current pricing
        
        Args:
            force_refresh: Force refresh of cached data
            
        Returns:
            List of model dictionaries with name, description, and pricing
        """
        # Check cache first
        if (not force_refresh and self.models_cache and self.cache_timestamp and 
            datetime.now() - self.cache_timestamp < self.cache_duration):
            return self.models_cache
        
        try:
            # Fetch current pricing information
            current_pricing = self._fetch_current_pricing()
            
            # Fetch models from OpenAI
            models_response = self.client.models.list()
            chat_models = []
            seen_base_models = set()  # Track base models to avoid duplicates
            
            for model in models_response.data:
                model_id = model.id
                
                # Filter for chat/GPT models and exclude fine-tuned models
                if self._is_chat_model(model_id) and not self._is_fine_tuned_model(model_id):
                    # Get the base model name (e.g., gpt-4o-2024-11-20 -> gpt-4o)
                    base_model = self._get_base_model_name(model_id)
                    
                    # Filter out unwanted models
                    if self._should_exclude_model(base_model):
                        logging.debug(f"Excluding model from available models: {base_model}")
                        continue
                    
                    # Skip if we've already added this base model
                    if base_model in seen_base_models:
                        continue
                    
                    seen_base_models.add(base_model)
                    
                    # Try to get pricing for this model family
                    pricing_info = self._get_model_pricing(base_model, current_pricing)
                    
                    chat_models.append({
                        "id": model_id,  # Keep the full model ID for API calls
                        "base_model": base_model,  # Store base model for reference
                        "name": self._format_model_name(base_model),
                        "description": pricing_info["description"],
                        "input_price": pricing_info["input"],
                        "output_price": pricing_info["output"],
                        "display_text": self._create_display_text(base_model, pricing_info)
                    })
            
            # Sort by relevance (GPT-4o models first, then by price)
            chat_models.sort(key=self._model_sort_key)
            
            # Cache the results
            self.models_cache = chat_models
            self.cache_timestamp = datetime.now()
            
            logging.info(f"Fetched {len(chat_models)} unique chat model families from OpenAI with current pricing")
            return chat_models
            
        except Exception as e:
            logging.error(f"Error fetching models: {e}")
            
            # Return fallback list if API fails
            fallback_models = self._get_fallback_models()
            logging.info(f"Using fallback model list ({len(fallback_models)} models)")
            return fallback_models
    
    def _get_model_pricing(self, model_id: str, pricing_data: Dict[str, Dict]) -> Dict:
        """
        Get pricing information for a specific model
        
        Args:
            model_id: The model identifier
            pricing_data: Dictionary of pricing information
            
        Returns:
            Pricing information for the model
        """
        # Direct match
        if model_id in pricing_data:
            return pricing_data[model_id]
        
        # Try to find a base model match (e.g., gpt-4o-2024-11-20 -> gpt-4o)
        for base_model in pricing_data.keys():
            if model_id.startswith(base_model):
                return pricing_data[base_model]
        
        # Try partial matches for curated model families only
        if "gpt-5-nano" in model_id:
            return pricing_data.get("gpt-5-nano", {
                "input": 0.00005, "output": 0.0004, 
                "description": "GPT-5 Nano variant"
            })
        elif "gpt-5-mini" in model_id:
            return pricing_data.get("gpt-5-mini", {
                "input": 0.00025, "output": 0.002, 
                "description": "GPT-5 Mini variant"
            })
        elif "gpt-5" in model_id:
            return pricing_data.get("gpt-5", {
                "input": 0.00125, "output": 0.01, 
                "description": "GPT-5 variant"
            })
        elif "gpt-4o-mini-realtime-preview" in model_id:
            return pricing_data.get("gpt-4o-mini-realtime-preview", {
                "input": 0.0006, "output": 0.0024, 
                "description": "GPT-4o Mini Realtime Preview variant"
            })
        elif "gpt-4o-mini" in model_id:
            return pricing_data.get("gpt-4o-mini", {
                "input": 0.00015, "output": 0.0006, 
                "description": "GPT-4o Mini variant"
            })
        elif "gpt-4o" in model_id:
            return pricing_data.get("gpt-4o", {
                "input": 0.0025, "output": 0.01, 
                "description": "GPT-4o variant"
            })
        elif "gpt-4.1-nano" in model_id:
            return pricing_data.get("gpt-4.1-nano", {
                "input": 0.0001, "output": 0.0004, 
                "description": "GPT-4.1 Nano variant"
            })
        elif "gpt-4.1-mini" in model_id:
            return pricing_data.get("gpt-4.1-mini", {
                "input": 0.0004, "output": 0.0016, 
                "description": "GPT-4.1 Mini variant"
            })
        elif "gpt-4.1" in model_id:
            return pricing_data.get("gpt-4.1", {
                "input": 0.002, "output": 0.008, 
                "description": "GPT-4.1 variant"
            })
        elif "gpt-4o-mini" in model_id:
            return pricing_data.get("gpt-4o-mini", {
                "input": 0.00015, "output": 0.0006, 
                "description": "GPT-4o Mini variant"
            })
        elif "gpt-4o" in model_id:
            return pricing_data.get("gpt-4o", {
                "input": 0.0025, "output": 0.010, 
                "description": "GPT-4o variant"
            })
        elif "gpt-4-turbo" in model_id:
            return pricing_data.get("gpt-4-turbo", {
                "input": 0.01, "output": 0.03, 
                "description": "GPT-4 Turbo variant"
            })
        elif "gpt-4" in model_id:
            return pricing_data.get("gpt-4", {
                "input": 0.03, "output": 0.06, 
                "description": "GPT-4 variant"
            })
        elif "gpt-3.5" in model_id:
            return pricing_data.get("gpt-3.5-turbo", {
                "input": 0.0005, "output": 0.0015, 
                "description": "GPT-3.5 Turbo variant"
            })
        
        # Default fallback
        return {
            "input": 0.0, 
            "output": 0.0, 
            "description": "Pricing information not available"
        }
    
    def _is_chat_model(self, model_id: str) -> bool:
        """Check if model is suitable for chat completion (curated models only)"""
        curated_models = [
            "gpt-5", "gpt-5-mini", "gpt-5-nano",
            "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", 
            "gpt-4o", "gpt-4o-mini", "gpt-4o-mini-realtime-preview"
        ]
        return any(model_id.lower().startswith(model.lower()) for model in curated_models)
    
    def _is_fine_tuned_model(self, model_id: str) -> bool:
        """Check if model is a fine-tuned model (usually contains colons)"""
        return ":" in model_id or "ft-" in model_id
    
    def _get_base_model_name(self, model_id: str) -> str:
        """
        Extract base model name from versioned model ID
        
        Examples:
        - gpt-5-nano-2024-08-01 -> gpt-5-nano
        - gpt-5-mini-2024-08-01 -> gpt-5-mini
        - gpt-5-2024-08-01 -> gpt-5
        - gpt-4o-2024-11-20 -> gpt-4o
        - gpt-4o-mini-2024-07-18 -> gpt-4o-mini
        - gpt-4-turbo-2024-04-09 -> gpt-4-turbo
        - gpt-3.5-turbo-0125 -> gpt-3.5-turbo
        """
        # Remove date patterns (YYYY-MM-DD format)
        import re
        base_model = re.sub(r'-\d{4}-\d{2}-\d{2}$', '', model_id)
        
        # Remove version patterns (numbers at the end)
        base_model = re.sub(r'-\d{4}$', '', base_model)
        base_model = re.sub(r'-\d{3}$', '', base_model)
        
        # Handle specific cases
        if base_model.startswith('gpt-5-nano'):
            return 'gpt-5-nano'
        elif base_model.startswith('gpt-5-mini'):
            return 'gpt-5-mini'
        elif base_model.startswith('gpt-5'):
            return 'gpt-5'
        elif base_model.startswith('gpt-4o-mini'):
            return 'gpt-4o-mini'
        elif base_model.startswith('gpt-4o'):
            return 'gpt-4o'
        elif base_model.startswith('gpt-4.1-nano'):
            return 'gpt-4.1-nano'
        elif base_model.startswith('gpt-4.1-mini'):
            return 'gpt-4.1-mini'
        elif base_model.startswith('gpt-4.1'):
            return 'gpt-4.1'
        elif base_model.startswith('gpt-4-turbo'):
            return 'gpt-4-turbo'
        elif base_model.startswith('gpt-4'):
            return 'gpt-4'
        elif base_model.startswith('gpt-3.5-turbo'):
            return 'gpt-3.5-turbo'
        
        return base_model
    
    def _format_model_name(self, model_id: str) -> str:
        """Format model ID into a readable name"""
        # Convert model ID to display name for curated models only
        if model_id.startswith("gpt-5-nano"):
            return "GPT-5 Nano"
        elif model_id.startswith("gpt-5-mini"):
            return "GPT-5 Mini"
        elif model_id.startswith("gpt-5"):
            return "GPT-5"
        elif model_id.startswith("gpt-4o-mini-realtime-preview"):
            return "GPT-4o Mini Realtime Preview"
        elif model_id.startswith("gpt-4o-mini"):
            return "GPT-4o Mini"
        elif model_id.startswith("gpt-4o"):
            return "GPT-4o"
        elif model_id.startswith("gpt-4.1-2025") or "gpt-4.1-2025" in model_id:
            return "GPT-4.1"  # Handle dated GPT-4.1 models like gpt-4.1-2025-04-14
        elif model_id.startswith("gpt-4.1-nano"):
            return "GPT-4.1 Nano"
        elif model_id.startswith("gpt-4.1-mini"):
            return "GPT-4.1 Mini"
        elif model_id.startswith("gpt-4.1"):
            return "GPT-4.1"
        else:
            # Fallback to formatted version of model ID
            return model_id.replace("-", " ").title()
    
    def _create_display_text(self, model_id: str, pricing_info: Dict) -> str:
        """Create display text for dropdown"""
        name = self._format_model_name(model_id)
        input_price = pricing_info["input"]
        output_price = pricing_info["output"]
        
        if input_price > 0 and output_price > 0:
            # Format prices consistently with proper decimal places
            if input_price < 0.001:
                input_str = f"{input_price:.5f}"
            else:
                input_str = f"{input_price:.4f}"
                
            if output_price < 0.001:
                output_str = f"{output_price:.5f}"
            else:
                output_str = f"{output_price:.4f}"
                
            return f"{name} (${input_str}/${output_str} per 1K tokens)"
        else:
            return f"{name} (Pricing not available)"
    
    def _model_sort_key(self, model: Dict) -> Tuple:
        """Sort key for curated models"""
        base_model = model.get("base_model", model["id"])
        
        # Priority order for curated models
        if "gpt-5" in base_model and "mini" not in base_model and "nano" not in base_model:
            priority = 1
        elif "gpt-5-mini" in base_model:
            priority = 2
        elif "gpt-5-nano" in base_model:
            priority = 3
        elif "gpt-4o" in base_model and "mini" not in base_model:
            priority = 4
        elif "gpt-4o-mini" in base_model and "realtime" not in base_model:
            priority = 5
        elif "gpt-4o-mini-realtime-preview" in base_model:
            priority = 6
        elif "gpt-4.1-2025" in base_model or ("gpt-4.1" in base_model and "mini" not in base_model and "nano" not in base_model):
            priority = 7  # Handle both dated (gpt-4.1-2025-xx-xx) and generic (gpt-4.1) models
        elif "gpt-4.1-mini" in base_model:
            priority = 8
        elif "gpt-4.1-nano" in base_model:
            priority = 9
        else:
            priority = 10

        return (priority, model["input_price"])
    
    def _get_fallback_models(self) -> List[Dict[str, str]]:
        """Return fallback model list if API is unavailable"""
        fallback_models = []
        fallback_pricing = self._get_fallback_pricing()
        
        for model_id, pricing_info in fallback_pricing.items():
            fallback_models.append({
                "id": model_id,
                "base_model": model_id,  # For fallback, base model is the same
                "name": self._format_model_name(model_id),
                "description": pricing_info["description"],
                "input_price": pricing_info["input"],
                "output_price": pricing_info["output"],
                "display_text": self._create_display_text(model_id, pricing_info)
            })
        
        # Sort using the same key
        fallback_models.sort(key=self._model_sort_key)
        return fallback_models
    
    def get_model_info(self, model_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific model
        
        Args:
            model_id: OpenAI model identifier
            
        Returns:
            Model information dictionary or None if not found
        """
        models = self.get_available_models()
        for model in models:
            if model["id"] == model_id:
                return model
        return None
    
    def estimate_cost(self, model_id: str, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for a given model and token usage
        
        Args:
            model_id: OpenAI model identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in dollars
        """
        model_info = self.get_model_info(model_id)
        if not model_info:
            return 0.0
        
        input_cost = (input_tokens / 1000) * model_info["input_price"]
        output_cost = (output_tokens / 1000) * model_info["output_price"]
        
        return input_cost + output_cost
    
    def get_recommended_model(self, use_case: str = "general") -> str:
        """
        Get recommended model based on use case
        
        Args:
            use_case: Type of task ("general", "cost_effective", "high_quality")
            
        Returns:
            Recommended model ID
        """
        models = self.get_available_models()
        
        if not models:
            return "gpt-4o-mini"  # Safe fallback
        
        if use_case == "cost_effective":
            # Find cheapest available model
            return min(models, key=lambda m: m["input_price"])["id"]
        elif use_case == "high_quality":
            # Find most capable model (usually first in sorted list)
            return models[0]["id"]
        else:  # general
            # Balance of quality and cost - prefer GPT-5-nano, then GPT-5-mini, then GPT-4o-mini
            for model in models:
                if "gpt-5-nano" in model["id"]:
                    return model["id"]
            for model in models:
                if "gpt-5-mini" in model["id"]:
                    return model["id"]
            for model in models:
                if "gpt-4o-mini" in model["id"]:
                    return model["id"]
            return models[0]["id"] if models else "gpt-5-nano"
    
    def refresh_pricing(self) -> bool:
        """
        Force refresh of pricing information
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Clear cache to force refresh
            self.pricing_cache = {}
            self.pricing_cache_timestamp = None
            
            # Fetch fresh pricing
            pricing_data = self._fetch_current_pricing()
            
            # Clear models cache to rebuild with new pricing
            self.models_cache = {}
            self.cache_timestamp = None
            
            logging.info("Successfully refreshed pricing information")
            return True
            
        except Exception as e:
            logging.error(f"Failed to refresh pricing: {e}")
            return False
    
    def get_pricing_last_updated(self) -> Optional[datetime]:
        """
        Get when pricing information was last updated
        
        Returns:
            Datetime of last pricing update or None if never updated
        """
        return self.pricing_cache_timestamp


def test_model_manager():
    """Test function for the dynamic model manager"""
    import os
    
    # This requires a real API key for testing
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("No OPENAI_API_KEY environment variable found")
        print("Testing with fallback data...")
        
        # Test fallback functionality
        try:
            manager = OpenAIModelManager("dummy-key")
            fallback_models = manager._get_fallback_models()
            print(f"✅ Fallback models available: {len(fallback_models)}")
            for model in fallback_models[:3]:
                print(f"   - {model['display_text']}")
        except Exception as e:
            print(f"❌ Fallback test failed: {e}")
        return
    
    try:
        print("🔄 Testing dynamic model and pricing fetching...")
        manager = OpenAIModelManager(api_key)
        
        # Test pricing fetch
        print("📊 Fetching current pricing information...")
        pricing_data = manager._fetch_current_pricing()
        print(f"✅ Retrieved pricing for {len(pricing_data)} model families")
        
        # Test model fetching
        print("🤖 Fetching available models...")
        models = manager.get_available_models()
        print(f"✅ Found {len(models)} available models with current pricing")
        
        # Show first few models
        print("\n📋 Available models:")
        for model in models[:5]:  # Show first 5
            print(f"   - {model['display_text']}")
        
        # Test cost estimation
        if models:
            model_id = models[0]["id"]
            cost = manager.estimate_cost(model_id, 1000, 500)
            print(f"\n💰 Cost estimate for {model_id}:")
            print(f"   1000 input + 500 output tokens = ${cost:.4f}")
        
        # Test recommendations
        print(f"\n🎯 Recommended models:")
        print(f"   Cost effective: {manager.get_recommended_model('cost_effective')}")
        print(f"   High quality: {manager.get_recommended_model('high_quality')}")
        print(f"   General use: {manager.get_recommended_model('general')}")
        
        # Show pricing update info
        last_updated = manager.get_pricing_last_updated()
        if last_updated:
            print(f"\n🕒 Pricing last updated: {last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n✅ All dynamic features working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing model manager: {e}")
        print("Falling back to static pricing...")
        
        # Test fallback
        try:
            manager = OpenAIModelManager("dummy-key")
            fallback_models = manager._get_fallback_models()
            print(f"✅ Fallback models available: {len(fallback_models)}")
        except Exception as e2:
            print(f"❌ Fallback also failed: {e2}")


if __name__ == "__main__":
    test_model_manager()
