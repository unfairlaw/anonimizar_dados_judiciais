# AWS Bedrock API Client

Complete toolkit for interacting with Claude models via AWS Bedrock API.

## 📦 Files

- `bedrock_api_client.py` - Full-featured Bedrock API client with examples
- `bedrock_simple_example.py` - Quick start example
- `requirements.txt` - Python dependencies
- `bedrock_token_calculator.py` - Token estimation utility
- `BEDROCK_API_README.md` - This documentation

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

```bash
aws configure
```

You'll need:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `us-east-1`)

### 3. Enable Bedrock Access

1. Go to AWS Bedrock Console
2. Request access to Claude models (if not already enabled)
3. Wait for approval (usually instant for Claude 3.5 Sonnet)

### 4. Test Your Setup

```bash
python3 bedrock_simple_example.py
```

This runs a simple test to verify your connection.

## 💡 Usage Examples

### Simple API Call

```bash
python3 bedrock_api_client.py example1
```

### Interactive Chat Mode

```bash
python3 bedrock_api_client.py interactive
```

### Run All Examples

```bash
python3 bedrock_api_client.py all
```

## 📝 Code Examples

### Example 1: Basic Query

```python
from bedrock_api_client import BedrockClient

# Initialize client
client = BedrockClient(model_id='claude-3-5-sonnet')

# Send a message
messages = [
    {
        'role': 'user',
        'content': 'Explain LGPD in one sentence.'
    }
]

result = client.invoke(messages, max_tokens=200)
print(result['content'])
print(f"Used {result['usage']['totalTokens']} tokens")
```

### Example 2: Streaming Response

```python
from bedrock_api_client import BedrockClient

client = BedrockClient(model_id='claude-3-5-sonnet')

messages = [
    {
        'role': 'user',
        'content': 'Write a short story about AI.'
    }
]

# Stream the response
for chunk in client.invoke_stream(messages):
    print(chunk, end='', flush=True)
```

### Example 3: Multi-turn Conversation

```python
from bedrock_api_client import BedrockClient

client = BedrockClient()

# Conversation history
messages = [
    {'role': 'user', 'content': 'What is a legal process?'},
    {'role': 'assistant', 'content': 'A legal process is...'},
    {'role': 'user', 'content': 'What are the main phases?'}
]

result = client.invoke(messages)
print(result['content'])
```

### Example 4: With System Prompt

```python
from bedrock_api_client import BedrockClient

client = BedrockClient()

system = "You are a legal expert specializing in Brazilian law."

messages = [
    {'role': 'user', 'content': 'Explain territorial jurisdiction.'}
]

result = client.invoke(
    messages,
    system=system,
    temperature=0.7,
    max_tokens=500
)

print(result['content'])
```

### Example 5: Process Judicial Data

```python
from bedrock_api_client import BedrockClient
from anonimizar_dados_judiciais import generate_petition_data

# Generate sample data
petition = generate_petition_data()

# Initialize client (using Haiku for cost efficiency)
client = BedrockClient(model_id='claude-3-haiku')

# Analyze the data
judicial_text = f"""
Process Data:
- Name: {petition['namePF']}
- CPF: {petition['cpf']}
- Process: {petition['judicialprocess']}
"""

messages = [
    {
        'role': 'user',
        'content': f'Validate this judicial data:\n{judicial_text}'
    }
]

result = client.invoke(messages)
print(result['content'])
```

## 🤖 Available Models

The client supports all Claude models on Bedrock:

| Short Name | Full Model ID | Use Case |
|------------|--------------|----------|
| `claude-3-5-sonnet` | anthropic.claude-3-5-sonnet-20241022-v2:0 | Best overall (recommended) |
| `claude-3-opus` | anthropic.claude-3-opus-20240229-v1:0 | Most capable, highest cost |
| `claude-3-sonnet` | anthropic.claude-3-sonnet-20240229-v1:0 | Balanced performance |
| `claude-3-haiku` | anthropic.claude-3-haiku-20240307-v1:0 | Fast and cost-efficient |

Usage:
```python
client = BedrockClient(model_id='claude-3-haiku')  # Use short name
# or
client = BedrockClient(model_id='anthropic.claude-3-haiku-20240307-v1:0')  # Full ID
```

## 💰 Pricing (as of 2024)

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| Claude 3.5 Sonnet | $3.00 | $15.00 |
| Claude 3 Opus | $15.00 | $75.00 |
| Claude 3 Sonnet | $3.00 | $15.00 |
| Claude 3 Haiku | $0.25 | $1.25 |

**Cost Examples:**
- 10,000 input + 2,000 output tokens with Haiku: ~$0.0028
- 10,000 input + 2,000 output tokens with Sonnet: ~$0.06
- 10,000 input + 2,000 output tokens with Opus: ~$0.30

## 🛠️ Features

### BedrockClient Class

```python
class BedrockClient:
    def __init__(self, region_name='us-east-1', model_id='claude-3-5-sonnet')

    def invoke(self, messages, max_tokens=4096, temperature=1.0, system=None)
    """Standard API call with full response"""

    def invoke_stream(self, messages, max_tokens=4096, temperature=1.0, system=None)
    """Streaming API call - yields text chunks"""
```

### Response Format

```python
{
    'content': 'The response text...',
    'role': 'assistant',
    'usage': {
        'inputTokens': 123,
        'outputTokens': 456,
        'totalTokens': 579
    },
    'stop_reason': 'end_turn',
    'metrics': {...}
}
```

## 📊 Token Usage Tracking

The client automatically:
- ✅ Estimates input tokens before API call
- ✅ Displays actual token usage after response
- ✅ Calculates cost for each request
- ✅ Integrates with token calculator

Example output:
```
📊 Estimated input tokens: 45

🚀 Calling Bedrock API...

📈 Token Usage:
   Input:  45 tokens
   Output: 123 tokens
   Total:  168 tokens
   Cost:   $0.000498
```

## 🔧 Advanced Usage

### Custom AWS Configuration

```python
import boto3
import os

# Use specific profile
os.environ['AWS_PROFILE'] = 'my-profile'

# Use specific region
client = BedrockClient(region_name='us-west-2')
```

### Error Handling

```python
from bedrock_api_client import BedrockClient
from botocore.exceptions import ClientError

client = BedrockClient()

try:
    result = client.invoke(messages)
except ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == 'ThrottlingException':
        print("Rate limited - retry later")
    elif error_code == 'ModelTimeoutException':
        print("Request timeout - try with fewer tokens")
    else:
        print(f"Error: {error_code}")
```

### Batch Processing

```python
from bedrock_api_client import BedrockClient

client = BedrockClient(model_id='claude-3-haiku')  # Use Haiku for batch

texts = ['Text 1', 'Text 2', 'Text 3']
results = []

for text in texts:
    messages = [{'role': 'user', 'content': f'Summarize: {text}'}]
    result = client.invoke(messages, max_tokens=100)
    results.append(result['content'])

print(f"Processed {len(results)} items")
```

### Save Conversation History

```python
import json
from bedrock_api_client import BedrockClient

client = BedrockClient()
conversation = []

# Chat loop
while True:
    user_msg = input("You: ")
    if user_msg.lower() == 'exit':
        break

    conversation.append({'role': 'user', 'content': user_msg})

    result = client.invoke(conversation)
    assistant_msg = result['content']

    conversation.append({'role': 'assistant', 'content': assistant_msg})
    print(f"Assistant: {assistant_msg}")

# Save conversation
with open('conversation.json', 'w') as f:
    json.dump(conversation, f, indent=2)
```

## 🔍 Debugging

Enable debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

View request/response:

```python
import boto3

boto3.set_stream_logger('botocore', level='DEBUG')
```

## ❗ Common Issues

### Issue: "NoCredentialsError"
**Solution:** Run `aws configure` and enter your credentials

### Issue: "AccessDeniedException"
**Solution:** Enable Bedrock models in AWS Console or request access

### Issue: "ModelNotReadyException"
**Solution:** Wait a few minutes after requesting model access

### Issue: "ThrottlingException"
**Solution:** You're hitting rate limits - implement backoff/retry

### Issue: "ValidationException: messages.role"
**Solution:** Ensure messages alternate between 'user' and 'assistant'

## 🧪 Testing

Test your setup:

```bash
# Test simple call
python3 bedrock_simple_example.py

# Test full client
python3 bedrock_api_client.py example1

# Test streaming
python3 bedrock_api_client.py example3

# Interactive test
python3 bedrock_api_client.py interactive
```

## 📚 Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Claude API Documentation](https://docs.anthropic.com/)
- [Boto3 Bedrock Runtime](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime.html)
- [AWS Pricing Calculator](https://calculator.aws/)

## 🔐 Security Best Practices

1. **Never commit AWS credentials** to version control
2. **Use IAM roles** when running on AWS infrastructure
3. **Limit IAM permissions** to only required Bedrock actions
4. **Rotate credentials** regularly
5. **Use AWS Secrets Manager** for production applications
6. **Monitor usage** with AWS CloudWatch

## 📦 Production Deployment

For production use, consider:

1. **Implement retry logic** with exponential backoff
2. **Add request/response logging**
3. **Set up CloudWatch metrics**
4. **Use AWS Lambda** for serverless execution
5. **Implement caching** for repeated queries
6. **Add rate limiting** to control costs
7. **Use AWS KMS** for encryption at rest

## 🤝 Integration Examples

### Flask API Endpoint

```python
from flask import Flask, request, jsonify
from bedrock_api_client import BedrockClient

app = Flask(__name__)
client = BedrockClient()

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])

    result = client.invoke(messages)

    return jsonify({
        'response': result['content'],
        'tokens': result['usage']['totalTokens']
    })

if __name__ == '__main__':
    app.run()
```

### AWS Lambda Function

```python
import json
from bedrock_api_client import BedrockClient

def lambda_handler(event, context):
    client = BedrockClient()

    messages = json.loads(event['body'])['messages']
    result = client.invoke(messages)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'response': result['content'],
            'usage': result['usage']
        })
    }
```

## 📄 License

This code is provided as-is for development and educational purposes.

---

**Need help?** Check the AWS Bedrock documentation or open an issue.
