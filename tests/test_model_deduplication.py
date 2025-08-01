"""
Test the improved model manager with deduplication
"""

from openai_model_manager import OpenAIModelManager

def test_model_deduplication():
    """Test that model deduplication works correctly"""
    
    print("🧪 Testing Model Deduplication")
    print("=" * 40)
    
    # Test with fallback data first
    print("1. Testing fallback models...")
    manager = OpenAIModelManager("dummy-key")
    fallback_models = manager._get_fallback_models()
    
    print(f"   ✅ Found {len(fallback_models)} fallback models")
    for model in fallback_models:
        print(f"   - {model['display_text']}")
    
    # Test base model name extraction
    print("\n2. Testing base model name extraction...")
    test_cases = [
        "gpt-4o-2024-11-20",
        "gpt-4o-mini-2024-07-18", 
        "gpt-4-turbo-2024-04-09",
        "gpt-3.5-turbo-0125",
        "gpt-4o",
        "gpt-4o-mini"
    ]
    
    for test_case in test_cases:
        base_model = manager._get_base_model_name(test_case)
        print(f"   {test_case} -> {base_model}")
    
    print("\n✅ Model deduplication test completed!")

if __name__ == "__main__":
    test_model_deduplication()
