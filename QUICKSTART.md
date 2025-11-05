# 🚀 Quick Start Guide - Bedrock API

Get started with AWS Bedrock API in 5 minutes!

## 1️⃣ Install Dependencies

```bash
pip install boto3
```

Or using the requirements file:
```bash
pip install -r requirements.txt
```

## 2️⃣ Configure AWS

```bash
aws configure
```

Enter:
- **AWS Access Key ID**: Your AWS access key
- **AWS Secret Access Key**: Your AWS secret key
- **Default region**: `us-east-1` (or your preferred region)
- **Output format**: `json`

## 3️⃣ Enable Bedrock (First Time Only)

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Click "Model access" in the left sidebar
3. Click "Manage model access"
4. Select Claude models:
   - ✅ Claude 3.5 Sonnet
   - ✅ Claude 3 Haiku (optional, for cost efficiency)
5. Click "Request model access"
6. Wait a few minutes for approval

## 4️⃣ Test Your Setup

```bash
python3 bedrock_simple_example.py
```

You should see:
```
Calling Bedrock API...

============================================================
RESPONSE:
============================================================
[Claude's response here]

============================================================
TOKEN USAGE:
============================================================
Input tokens:  12
Output tokens: 45
Total tokens:  57
============================================================
```

## 5️⃣ Try Interactive Mode

```bash
python3 bedrock_api_client.py interactive
```

Chat with Claude directly from your terminal!

---

## 📚 What's Next?

### Run Examples
```bash
# Simple query
python3 bedrock_api_client.py example1

# Streaming response
python3 bedrock_api_client.py example3

# All examples
python3 bedrock_api_client.py all
```

### Use in Your Code

```python
from bedrock_api_client import BedrockClient

# Create client
client = BedrockClient(model_id='claude-3-5-sonnet')

# Send message
messages = [
    {'role': 'user', 'content': 'Hello!'}
]

result = client.invoke(messages)
print(result['content'])
```

### Calculate Tokens

```bash
# Estimate tokens for text
python3 calculate_tokens.py "Your text here"

# With cost estimate
python3 calculate_tokens.py --cost "Your text here"

# From file
python3 calculate_tokens.py --file yourfile.txt
```

---

## 🛠️ Full Setup Script

Run everything at once:

```bash
chmod +x setup_bedrock.sh
./setup_bedrock.sh
```

This will:
- ✅ Check Python installation
- ✅ Install dependencies
- ✅ Verify AWS credentials
- ✅ Test Bedrock connection

---

## ❓ Troubleshooting

### "NoCredentialsError"
**Problem:** AWS credentials not configured
**Solution:** Run `aws configure`

### "AccessDeniedException"
**Problem:** No access to Bedrock
**Solution:** Enable model access in AWS Console (step 3 above)

### "ModuleNotFoundError: No module named 'boto3'"
**Problem:** boto3 not installed
**Solution:** Run `pip install boto3`

### "ValidationException"
**Problem:** Invalid request format
**Solution:** Check message format matches examples

---

## 💰 Cost Management

Start with cost-efficient models:

```python
# Use Haiku for testing (cheapest)
client = BedrockClient(model_id='claude-3-haiku')

# Use Sonnet for production (balanced)
client = BedrockClient(model_id='claude-3-5-sonnet')

# Use Opus for complex tasks (most capable)
client = BedrockClient(model_id='claude-3-opus')
```

**Pricing comparison:**
- Haiku: ~$0.001 per 10K tokens
- Sonnet: ~$0.06 per 10K tokens
- Opus: ~$0.30 per 10K tokens

---

## 📖 Documentation

- `BEDROCK_API_README.md` - Full API documentation
- `TOKEN_CALCULATOR_README.md` - Token calculator guide
- `bedrock_api_client.py` - Complete client with examples
- `bedrock_simple_example.py` - Minimal working example

---

## 🎯 Common Use Cases

### 1. Document Analysis
```python
client = BedrockClient(model_id='claude-3-haiku')
messages = [{'role': 'user', 'content': f'Analyze: {document_text}'}]
result = client.invoke(messages)
```

### 2. Chatbot
```python
client = BedrockClient()
conversation = []

while True:
    user_input = input("You: ")
    conversation.append({'role': 'user', 'content': user_input})

    result = client.invoke(conversation)
    conversation.append({'role': 'assistant', 'content': result['content']})

    print(f"Bot: {result['content']}")
```

### 3. Batch Processing
```python
client = BedrockClient(model_id='claude-3-haiku')

for item in items:
    messages = [{'role': 'user', 'content': f'Process: {item}'}]
    result = client.invoke(messages, max_tokens=100)
    print(result['content'])
```

---

## ✅ You're Ready!

Your Bedrock API client is ready to use. Start building amazing AI-powered applications! 🎉

**Need help?** Check:
- `BEDROCK_API_README.md` for detailed documentation
- [AWS Bedrock Docs](https://docs.aws.amazon.com/bedrock/)
- [Claude API Docs](https://docs.anthropic.com/)
