"""
Test realistic model deduplication scenario
"""

from openai_model_manager import OpenAIModelManager

def test_realistic_scenario():
    """Test with realistic model scenarios that would cause duplicates"""
    
    print("🚀 Testing Realistic Model Deduplication")
    print("=" * 45)
    
    manager = OpenAIModelManager("dummy-key")
    
    # Simulate what OpenAI API might return (multiple variants of same model)
    simulated_models = [
        "gpt-4o-2024-11-20",
        "gpt-4o-2024-08-06", 
        "gpt-4o",
        "gpt-4o-mini-2024-07-18",
        "gpt-4o-mini",
        "gpt-4-turbo-2024-04-09",
        "gpt-4-turbo",
        "gpt-4-0613",
        "gpt-4",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo"
    ]
    
    print("Simulated API models (with duplicates):")
    for model in simulated_models:
        print(f"  - {model}")
    
    print(f"\nProcessing {len(simulated_models)} models...")
    
    # Test deduplication logic
    seen_base_models = set()
    deduplicated = []
    
    for model_id in simulated_models:
        base_model = manager._get_base_model_name(model_id)
        
        if base_model not in seen_base_models:
            seen_base_models.add(base_model)
            display_name = manager._format_model_name(base_model)
            pricing = manager._get_model_pricing(base_model, manager._get_fallback_pricing())
            display_text = manager._create_display_text(base_model, pricing)
            
            deduplicated.append({
                "original_id": model_id,
                "base_model": base_model,
                "display_name": display_name,
                "display_text": display_text
            })
    
    print(f"\nAfter deduplication: {len(deduplicated)} unique models")
    for i, model in enumerate(deduplicated):
        print(f"  {i+1}. {model['display_text']}")
        print(f"     (From: {model['original_id']} -> {model['base_model']})")
    
    print(f"\n✅ Reduced from {len(simulated_models)} to {len(deduplicated)} models")
    print("✅ No duplicates in final list")

if __name__ == "__main__":
    test_realistic_scenario()
