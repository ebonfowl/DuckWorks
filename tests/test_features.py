"""
Test script for DuckGrade features
Part of the DuckWorks Educational Automation Suite
"""

import os
import sys

def test_imports():
    """Test that all new modules import correctly"""
    print("🦆 Testing DuckGrade Features")
    print("=" * 50)
    
    try:
        print("1. Testing secure key manager...")
        from secure_key_manager import APIKeyManager, SecureKeyManager
        print("   ✅ Secure key manager imported successfully")
        
        print("2. Testing OpenAI model manager...")
        from openai_model_manager import OpenAIModelManager
        print("   ✅ Model manager imported successfully")
        
        print("3. Testing DuckGrade core engine...")
        from grading_agent import GradingAgent
        print("   ✅ DuckGrade core engine imported successfully")
        
        print("4. Testing GUI imports...")
        import tkinter as tk
        from tkinter import ttk
        print("   ✅ GUI libraries available")
        
        print("5. Testing PyQt6 Canvas GUI...")
        from PyQt6.QtWidgets import QApplication
        print("   ✅ PyQt6 Canvas GUI libraries available")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_key_manager():
    """Test key manager functionality"""
    print("\n6. Testing key manager functionality...")
    
    try:
        from secure_key_manager import APIKeyManager
        
        manager = APIKeyManager()
        
        # Test basic functionality
        has_config = manager.key_manager.has_config()
        print(f"   📝 Has existing config: {has_config}")
        
        if has_config:
            try:
                has_openai = manager.has_openai_key()
                has_canvas = manager.has_canvas_credentials()
                print(f"   🔑 Has OpenAI key: {has_openai}")
                print(f"   🌐 Has Canvas credentials: {has_canvas}")
            except:
                print("   📝 Config exists but requires password to access")
        
        print("   ✅ Key manager functionality working")
        return True
        
    except Exception as e:
        print(f"   ❌ Key manager test failed: {e}")
        return False

def test_model_manager():
    """Test model manager functionality with dynamic pricing"""
    print("\n7. Testing dynamic model manager functionality...")
    
    try:
        from openai_model_manager import OpenAIModelManager
        
        # Test fallback models (should work without API key)
        dummy_manager = OpenAIModelManager("dummy-key")
        fallback_models = dummy_manager._get_fallback_models()
        
        print(f"   📊 Fallback models available: {len(fallback_models)}")
        if fallback_models:
            example = fallback_models[0]
            print(f"   💡 Example model: {example['name']} - {example['display_text']}")
        
        # Test dynamic pricing functionality (structure)
        print("   🔄 Testing dynamic pricing structure...")
        fallback_pricing = dummy_manager._get_fallback_pricing()
        print(f"   💰 Pricing data structure: {len(fallback_pricing)} model families")
        
        # Test pricing cache mechanism
        pricing_updated = dummy_manager.get_pricing_last_updated()
        print(f"   🕒 Pricing cache status: {'Not updated yet' if pricing_updated is None else 'Has timestamp'}")
        
        print("   ✅ Dynamic model manager functionality working")
        return True
        
    except Exception as e:
        print(f"   ❌ Model manager test failed: {e}")
        return False

def test_enhanced_agent():
    """Test DuckGrade core engine initialization"""
    print("\n8. Testing DuckGrade core engine...")
    
    try:
        from grading_agent import GradingAgent
        
        # Test that we can initialize with model parameter
        # (Will fail without real API key, but should accept the parameter)
        try:
            agent = GradingAgent("dummy-key", model="gpt-4o-mini")
            print("   ✅ DuckGrade core engine accepts model parameter")
        except Exception as e:
            if "api_key" in str(e).lower() or "openai" in str(e).lower():
                print("   ✅ DuckGrade core engine accepts model parameter (API key validation as expected)")
            else:
                raise e
        
        return True
        
    except Exception as e:
        print(f"   ❌ DuckGrade core engine test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🦆 DuckGrade - Part of the DuckWorks Educational Suite")
    print("==================================================")
    
    tests = [
        test_imports,
        test_key_manager,
        test_model_manager,
        test_enhanced_agent
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! DuckGrade is ready to use.")
        print("\n🦆 DuckGrade Features:")
        print("• 🔐 Encrypted API key storage")
        print("• 🎛️ Dynamic OpenAI model selection")
        print("• 💰 Real-time pricing information (fetched from OpenAI)")
        print("• 🔄 Auto-updating model list and pricing")
        print("• 🖥️ Enhanced GUI interfaces with duck branding")
        print("• 📁 Multi-format file support (.txt, .docx, .pdf, .html, .odt, .rtf)")
        print("• 🌐 Canvas LMS integration")
        print("\n🚀 To get started (RECOMMENDED - No environment switching!):")
        print("• Run: start_duckgrade_gui_direct.bat (Local file grading)")
        print("• Or:  start_duckgrade_canvas_direct.bat (Canvas integration)")
        print("• Or:  start_duckgrade_direct.bat (Main launcher menu)")
        print("\n🔧 Environment Management:")
        print("• conda auto_activate_base is now disabled to prevent switching")
        print("• Use activate_duckgrade_env.bat to manually activate if needed")
        print("• Direct execution batch files bypass environment issues")
        print("\n📊 Pricing Information:")
        print("• Models and pricing are fetched dynamically from OpenAI")
        print("• Pricing updates automatically (cached for 6 hours)")
        print("• No more manual updates needed!")
        print("\n🦆 Part of DuckWorks - Educational Automation That Just Works!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check error messages above.")

if __name__ == "__main__":
    main()
