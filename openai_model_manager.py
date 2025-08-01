"""
OpenAI Model Manager
Dynamically fetches available models and pricing information
"""

import openai
import requests
import json
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
        Fetch current OpenAI pricing using ChatGPT itself to get up-to-date information
        
        Returns:
            Dictionary of model pricing information
        """
        # Check cache first
        if (self.pricing_cache and self.pricing_cache_timestamp and 
            datetime.now() - self.pricing_cache_timestamp < timedelta(days=1)):
            return self.pricing_cache
        
        try:
            pricing_prompt = """
            Please provide the current OpenAI API pricing for chat completion models as of today's date. 
            I need the input and output token costs per 1000 tokens in USD for each model.
            
            Please respond with a JSON object in this exact format:
            {
                "gpt-4o": {"input": 0.0025, "output": 0.010, "description": "Most capable model, best for complex tasks"},
                "gpt-4o-mini": {"input": 0.00015, "output": 0.0006, "description": "Faster, cheaper version of GPT-4o"},
                "gpt-4-turbo": {"input": 0.01, "output": 0.03, "description": "Previous generation turbo model"},
                "gpt-4": {"input": 0.03, "output": 0.06, "description": "Original GPT-4 model"},
                "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015, "description": "Fast and efficient for most tasks"}
            }
            
            Include all currently available chat completion models. Use the most recent pricing information available.
            Only include the JSON object in your response, no other text.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Use the cheapest model for this query
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides accurate, up-to-date OpenAI API pricing information. Respond only with valid JSON."},
                    {"role": "user", "content": pricing_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            pricing_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            start_idx = pricing_text.find('{')
            end_idx = pricing_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = pricing_text[start_idx:end_idx]
                pricing_data = json.loads(json_str)
                
                # Cache the results
                self.pricing_cache = pricing_data
                self.pricing_cache_timestamp = datetime.now()
                
                logging.info(f"Fetched current pricing for {len(pricing_data)} models")
                return pricing_data
            else:
                raise ValueError("Could not extract JSON from pricing response")
                
        except Exception as e:
            logging.warning(f"Failed to fetch current pricing: {e}")
            # Return fallback pricing if API call fails
            return self._get_fallback_pricing()
    
    def _get_fallback_pricing(self) -> Dict[str, Dict]:
        """
        Fallback pricing data if dynamic fetching fails
        """
        return {
            "gpt-4o": {"input": 0.0025, "output": 0.010, "description": "Most capable model, best for complex tasks"},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006, "description": "Faster, cheaper version of GPT-4o"},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03, "description": "Previous generation turbo model"},
            "gpt-4": {"input": 0.03, "output": 0.06, "description": "Original GPT-4 model"},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015, "description": "Fast and efficient for most tasks"},
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
        
        # Try partial matches for model families
        if "gpt-4o-mini" in model_id:
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
        """Check if model is suitable for chat completion"""
        chat_keywords = ["gpt-4", "gpt-3.5", "gpt-4o"]
        return any(keyword in model_id.lower() for keyword in chat_keywords)
    
    def _is_fine_tuned_model(self, model_id: str) -> bool:
        """Check if model is a fine-tuned model (usually contains colons)"""
        return ":" in model_id or "ft-" in model_id
    
    def _get_base_model_name(self, model_id: str) -> str:
        """
        Extract base model name from versioned model ID
        
        Examples:
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
        if base_model.startswith('gpt-4o-mini'):
            return 'gpt-4o-mini'
        elif base_model.startswith('gpt-4o'):
            return 'gpt-4o'
        elif base_model.startswith('gpt-4-turbo'):
            return 'gpt-4-turbo'
        elif base_model.startswith('gpt-4'):
            return 'gpt-4'
        elif base_model.startswith('gpt-3.5-turbo'):
            return 'gpt-3.5-turbo'
        
        return base_model
    
    def _format_model_name(self, model_id: str) -> str:
        """Format model ID into a readable name"""
        # Convert model ID to display name with specific ordering
        # Check longer patterns first to avoid false matches
        if model_id.startswith("gpt-4o-mini"):
            return "GPT-4o Mini"
        elif model_id.startswith("gpt-4o"):
            return "GPT-4o"
        elif model_id.startswith("gpt-4-turbo"):
            return "GPT-4 Turbo"
        elif model_id.startswith("gpt-4"):
            return "GPT-4"
        elif model_id.startswith("gpt-3.5-turbo"):
            return "GPT-3.5 Turbo"
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
        """Sort key for models (GPT-4o first, then by input price)"""
        base_model = model.get("base_model", model["id"])
        
        # Priority order
        if "gpt-4o" in base_model and "mini" not in base_model:
            priority = 1
        elif "gpt-4o-mini" in base_model:
            priority = 2
        elif "gpt-4-turbo" in base_model:
            priority = 3
        elif "gpt-4" in base_model:
            priority = 4
        elif "gpt-3.5" in base_model:
            priority = 5
        else:
            priority = 6
        
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
            # Balance of quality and cost - prefer GPT-4o Mini
            for model in models:
                if "gpt-4o-mini" in model["id"]:
                    return model["id"]
            return models[0]["id"] if models else "gpt-4o-mini"
    
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
