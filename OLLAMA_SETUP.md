# Ollama Integration Setup Guide

This guide will help you integrate Ollama with your Sophia AI Assistant.

## Prerequisites

- ✅ Ollama installed on your system (C: drive)
- ✅ Sophia AI Assistant project on G: drive
- ✅ Python 3.12 installed

## Step 1: Start Ollama Service

Open a new Command Prompt and run:
```sh
ollama serve
```

Keep this window open - Ollama needs to keep running.

## Step 2: Pull a Model

In another Command Prompt window, pull a model:
```sh
ollama pull llama2
```

Or try a smaller model:
```sh
ollama pull phi3
```

## Step 3: Test Ollama Integration

Navigate to your project directory:
```sh
cd /d G:\Sophia-AI-Assistant-master
```

Run the test script:
```sh
python test_ollama.py
```

This will test:
- ✅ Ollama service connection
- ✅ Model availability
- ✅ Basic query processing
- ✅ Sophia AI integration

## Step 4: Run Sophia AI Assistant

Once the tests pass, run your assistant:
```sh
python main.py
```

## How It Works

1. **Primary AI**: Sophia will try to use OpenAI first (if API key is configured)
2. **Fallback AI**: If OpenAI fails, Sophia will automatically use Ollama
3. **Local Processing**: All AI processing happens locally on your machine

## Available Models

You can use any model available in Ollama:
- `llama2` - Good general purpose model
- `phi3` - Smaller, faster model
- `mistral` - High quality responses
- `codellama` - Good for programming questions

## Troubleshooting

### Ollama service not running
```
Error: Cannot connect to Ollama service
```
**Solution**: Run `ollama serve` in a separate terminal

### No models available
```
Error: No models found
```
**Solution**: Pull a model with `ollama pull llama2`

### Model not found
```
Error: Model 'llama2' not found
```
**Solution**: Check available models with `ollama list`

## Benefits

- 🚀 **Faster responses** - No internet dependency
- 🔒 **Privacy** - All processing happens locally
- 💰 **Cost-effective** - No API costs
- 🎯 **Customizable** - Use any Ollama model

## Commands

### Check Ollama status
```sh
ollama list
```

### Pull a new model
```sh
ollama pull <model-name>
```

### Remove a model
```sh
ollama rm <model-name>
```

### Test a model directly
```sh
ollama run llama2
```

## Integration Details

The integration is located in:
- `engine/ollama_integration.py` - Core Ollama functionality
- `engine/ai_assistant.py` - Updated to use Ollama as fallback
- `test_ollama.py` - Test script

Sophia will automatically detect which AI service is available and use the best option for each query. 