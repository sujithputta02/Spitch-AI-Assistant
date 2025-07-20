#!/usr/bin/env python3
"""
Script to pull Ollama models using the API
"""

import requests
import json
import time

def pull_model(model_name="llama2"):
    """Pull a model using Ollama API"""
    print(f"🔄 Pulling model: {model_name}")
    print("This may take several minutes depending on your internet connection...")
    
    try:
        # Start the pull request
        response = requests.post(
            "http://localhost:11434/api/pull",
            json={"name": model_name},
            stream=True
        )
        
        if response.status_code == 200:
            print("✅ Pull started successfully")
            
            # Monitor the pull progress
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        
                        if 'status' in data:
                            print(f"📦 {data['status']}")
                        
                        if 'completed_at' in data:
                            print(f"✅ Model {model_name} pulled successfully!")
                            return True
                            
                    except json.JSONDecodeError:
                        continue
        else:
            print(f"❌ Failed to start pull: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error pulling model: {e}")
        return False

def list_models():
    """List available models"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            if models:
                print("📋 Available models:")
                for model in models:
                    print(f"  - {model['name']}")
            else:
                print("📋 No models available")
        else:
            print(f"❌ Failed to list models: {response.status_code}")
    except Exception as e:
        print(f"❌ Error listing models: {e}")

if __name__ == "__main__":
    print("🚀 Ollama Model Puller")
    print("=" * 40)
    
    # List current models
    print("\nCurrent models:")
    list_models()
    
    # Ask user which model to pull
    print("\nAvailable models to pull:")
    print("1. llama2 (4GB - Good general purpose)")
    print("2. phi3 (2GB - Smaller, faster)")
    print("3. mistral (4GB - High quality)")
    print("4. codellama (6GB - Programming focused)")
    
    choice = input("\nEnter model number (1-4) or model name: ").strip()
    
    model_map = {
        "1": "llama2",
        "2": "phi3", 
        "3": "mistral",
        "4": "codellama"
    }
    
    if choice in model_map:
        model_name = model_map[choice]
    else:
        model_name = choice
    
    print(f"\nPulling model: {model_name}")
    
    # Pull the model
    success = pull_model(model_name)
    
    if success:
        print("\n🎉 Model pulled successfully!")
        print("\nUpdated model list:")
        list_models()
        
        print("\nNext steps:")
        print("1. Test the integration: python test_ollama.py")
        print("2. Run Sophia: python main.py")
    else:
        print("\n❌ Failed to pull model")
        print("Please check your internet connection and try again.") 