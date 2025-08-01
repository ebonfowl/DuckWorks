"""
Comprehensive test of the model manager fixes
"""

from openai_model_manager import OpenAIModelManager

def test_comprehensive():
    """Test the model manager comprehensively"""
    
    print("🔧 Testing Model Manager Fixes")
    print("=" * 50)
    
    # Test with dummy key (fallback mode)
    print("1. Testing fallback models (no duplicates expected)...")
    manager = OpenAIModelManager("dummy-key")
    
    # Get fallback models
    models = manager.get_available_models()
    
    print(f"   Found {len(models)} models:")
    
    # Check for duplicates by name
    seen_names = set()
    duplicates = []
    
    for i, model in enumerate(models):
        name = model['name']
        display = model['display_text']
        base_model = model.get('base_model', 'N/A')
        
        print(f"   {i+1}. {display}")
        print(f"      ID: {model['id']}, Base: {base_model}")
        
        if name in seen_names:
            duplicates.append(name)
        seen_names.add(name)
    
    if duplicates:
        print(f"\n   ❌ Found duplicate names: {duplicates}")
    else:
        print(f"\n   ✅ No duplicate model names found")
    
    # Test base model extraction
    print("\n2. Testing base model name extraction...")
    test_models = [
        "gpt-4o-2024-11-20",
        "gpt-4o-mini-2024-07-18",
        "gpt-4-turbo-2024-04-09", 
        "gpt-3.5-turbo-0125",
        "gpt-4-0613",
        "gpt-4o",
        "gpt-4o-mini"
    ]
    
    for test_model in test_models:
        base = manager._get_base_model_name(test_model)
        pricing = manager._get_model_pricing(base, manager._get_fallback_pricing())
        print(f"   {test_model}")
        print(f"   -> Base: {base}")
        print(f"   -> Pricing: ${pricing['input']:.5f}/${pricing['output']:.5f}")
        print()

if __name__ == "__main__":
    test_comprehensive()
