#!/usr/bin/env python3
"""
Test script for Ollama integration with Sophia AI Assistant
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ollama_integration():
    """Test Ollama integration"""
    print("🧪 Testing Ollama Integration with Sophia AI Assistant")
    print("=" * 60)
    
    try:
        # Test 1: Import Ollama integration
        print("\n1. Testing import...")
        from engine.ollama_integration import sophia_ollama
        print("✅ Ollama integration module imported successfully")
        
        # Test 2: Check if Ollama service is running
        print("\n2. Testing Ollama service connection...")
        if sophia_ollama.test_connection():
            print("✅ Ollama service is running")
        else:
            print("❌ Ollama service is not running")
            print("   Please start Ollama with: ollama serve")
            return False
        
        # Test 3: Get available models
        print("\n3. Testing model availability...")
        models = sophia_ollama.get_available_models()
        if models:
            print(f"✅ Available models: {models}")
        else:
            print("❌ No models found")
            print("   Please pull a model with: ollama pull llama2")
            return False
        
        # Test 4: Test basic query
        print("\n4. Testing basic query...")
        test_query = "Hello, how are you?"
        print(f"   Query: {test_query}")
        
        response = sophia_ollama.process_query(test_query)
        print(f"   Response: {response}")
        
        if response and "sorry" not in response.lower():
            print("✅ Basic query test passed")
        else:
            print("⚠️  Basic query test had issues")
        
        # Test 5: Test Sophia AI integration
        print("\n5. Testing Sophia AI integration...")
        from engine.ai_assistant import sophia_ai
        
        result = sophia_ai.process_command("What is the weather like?")
        print(f"   AI Source: {result.get('ai_source', 'Unknown')}")
        print(f"   Response: {result.get('response', 'No response')}")
        
        if result.get('ai_source') in ['OpenAI', 'Ollama']:
            print("✅ Sophia AI integration test passed")
        else:
            print("⚠️  Sophia AI integration test had issues")
        
        print("\n" + "=" * 60)
        print("🎉 Ollama integration test completed!")
        print("\nNext steps:")
        print("1. Start Ollama: ollama serve")
        print("2. Pull a model: ollama pull llama2")
        print("3. Run Sophia: python main.py")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_ollama_commands():
    """Test specific Ollama commands"""
    print("\n🔧 Testing Ollama Commands")
    print("=" * 40)
    
    try:
        from engine.ollama_integration import sophia_ollama
        
        # Test model info
        print("\nTesting model info...")
        model_info = sophia_ollama.ollama.get_model_info("llama2")
        if model_info.get("success"):
            print("✅ Model info retrieved successfully")
        else:
            print(f"⚠️  Model info error: {model_info.get('error', 'Unknown')}")
        
        # Test chat with context
        print("\nTesting chat with context...")
        messages = [
            {"role": "user", "content": "My name is John"},
            {"role": "assistant", "content": "Nice to meet you, John!"},
            {"role": "user", "content": "What's my name?"}
        ]
        
        chat_result = sophia_ollama.ollama.chat_with_context(messages)
        if chat_result.get("success"):
            print("✅ Chat with context test passed")
            print(f"   Response: {chat_result.get('response', '')[:100]}...")
        else:
            print(f"⚠️  Chat with context error: {chat_result.get('error', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Command test error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Ollama Integration Tests")
    
    # Run main integration test
    success = test_ollama_integration()
    
    if success:
        # Run additional command tests
        test_ollama_commands()
    
    print("\n✨ Test session completed!") 