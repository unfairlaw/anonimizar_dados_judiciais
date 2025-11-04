# AWS Bedrock Integration Guide

This guide explains how to use AWS Bedrock with the RAG Ecosystem for fully AWS-native, secure, and cost-effective deployments.

## 🌟 Why Use Bedrock?

### Benefits

| Feature | Bedrock | OpenAI/Anthropic Direct |
|---------|---------|------------------------|
| **Data Privacy** | Stays in your AWS account | Sent to external APIs |
| **Security** | AWS IAM roles, VPC support | API keys only |
| **Cost** | Pay-per-token, volume discounts | Pay-per-token |
| **Models** | Claude, Llama, Titan, Cohere | Limited to provider |
| **Latency** | Lower (same region) | Higher (internet) |
| **Compliance** | HIPAA, SOC, PCI DSS ready | Varies |

### Cost Comparison (per 1M tokens)

| Model | Input | Output | Use Case |
|-------|-------|--------|----------|
| **Claude 3 Haiku** | $0.25 | $1.25 | Fast, routine queries |
| **Claude 3 Sonnet** | $3.00 | $15.00 | Balanced (recommended) |
| **Claude 3 Opus** | $15.00 | $75.00 | Complex reasoning |
| **Titan Text Express** | $0.13 | $0.17 | Budget-friendly |
| **Llama 3 70B** | $0.99 | $0.99 | Open source |

**Embeddings:**
- **Titan Embed Text**: $0.10 per 1M tokens (1536 dimensions)
- **Cohere Embed**: $0.10 per 1M tokens (1024 dimensions)

## 🚀 Quick Start

### 1. Enable Bedrock Models

```bash
# Go to AWS Console > Bedrock > Model access
# Or use CLI:
aws bedrock list-foundation-models --region us-east-1

# Request model access (one-time)
# Visit: https://console.aws.amazon.com/bedrock/
# Click "Model access" and request access to:
#   - Anthropic Claude models
#   - Amazon Titan models
```

### 2. Configure RAG Ecosystem

**Option A: Environment Variables**

```bash
# Create .env file
cat > .env <<EOF
LLM_PROVIDER=bedrock
BEDROCK_REGION=us-east-1
BEDROCK_LLM_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v1

EMBEDDING_PROVIDER=bedrock
EMBEDDING_MODEL=amazon.titan-embed-text-v1
EMBEDDING_DIMENSION=1536

# S3 Configuration
S3_BUCKET_NAME=my-rag-bucket
EOF
```

**Option B: Programmatic**

```python
from rag_ecosystem.config.settings import get_settings

settings = get_settings()
settings.llm_provider = "bedrock"
settings.bedrock_llm_model = "anthropic.claude-3-sonnet-20240229-v1:0"
settings.bedrock_embedding_model = "amazon.titan-embed-text-v1"
```

### 3. Set IAM Permissions

**For Lambda:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/*"
    }
  ]
}
```

**For EC2:**

Attach the above policy to your EC2 instance role.

### 4. Test It

```python
from rag_ecosystem.agents.agentic_rag import AgenticRAG
from rag_ecosystem.components.indexing import DocumentIndexer

# Index documents
indexer = DocumentIndexer()
indexer.index_from_text("AWS Bedrock is a fully managed service...")

# Query (uses Bedrock by default)
rag = AgenticRAG()
result = rag.query("What is AWS Bedrock?")
print(result['answer'])
```

## 📊 Available Models

### LLM Models

#### Claude 3 (Anthropic) - Recommended

```python
# Haiku - Fast & Cheap
BEDROCK_LLM_MODEL=anthropic.claude-3-haiku-20240307-v1:0

# Sonnet - Balanced (default)
BEDROCK_LLM_MODEL=anthropic.claude-3-sonnet-20240229-v1:0

# Opus - Most Capable
BEDROCK_LLM_MODEL=anthropic.claude-3-opus-20240229-v1:0
```

**Features:**
- 200K context window
- Strong reasoning capabilities
- Low hallucination rate
- Streaming support

#### Amazon Titan

```python
# Titan Text Express
BEDROCK_LLM_MODEL=amazon.titan-text-express-v1

# Titan Text Lite
BEDROCK_LLM_MODEL=amazon.titan-text-lite-v1
```

**Features:**
- 8K context window
- Cost-effective
- AWS-native

#### Meta Llama 3

```python
# Llama 3 70B
BEDROCK_LLM_MODEL=meta.llama3-70b-instruct-v1:0

# Llama 3 8B
BEDROCK_LLM_MODEL=meta.llama3-8b-instruct-v1:0
```

**Features:**
- Open source
- Good performance
- 8K context window

#### Cohere Command R+

```python
BEDROCK_LLM_MODEL=cohere.command-r-plus-v1:0
```

**Features:**
- RAG-optimized
- Multi-lingual
- 128K context window

### Embedding Models

#### Amazon Titan Embeddings (Default)

```python
BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v1
EMBEDDING_DIMENSION=1536
```

**Best for:**
- English text
- General purpose
- Cost-effective

#### Cohere Embed

```python
# English
BEDROCK_EMBEDDING_MODEL=cohere.embed-english-v3
EMBEDDING_DIMENSION=1024

# Multilingual
BEDROCK_EMBEDDING_MODEL=cohere.embed-multilingual-v3
EMBEDDING_DIMENSION=1024
```

**Best for:**
- Multilingual support
- Semantic search
- Domain adaptation

## 🔐 Security Best Practices

### 1. Use IAM Roles (Not API Keys)

```bash
# Lambda - automatically uses execution role
# EC2 - attach instance profile

# Never hardcode credentials!
```

### 2. Restrict Model Access

```json
{
  "Effect": "Allow",
  "Action": "bedrock:InvokeModel",
  "Resource": [
    "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
  ]
}
```

### 3. Enable VPC Endpoints

```bash
# Create VPC endpoint for Bedrock
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-xxxxx \
    --service-name com.amazonaws.us-east-1.bedrock-runtime \
    --route-table-ids rtb-xxxxx
```

### 4. Enable CloudTrail Logging

```bash
# All Bedrock API calls are logged
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=EventName,AttributeValue=InvokeModel
```

## 💰 Cost Optimization

### 1. Choose the Right Model

```python
# For simple queries - use Haiku
if query_complexity == "simple":
    model = "anthropic.claude-3-haiku-20240307-v1:0"

# For complex reasoning - use Sonnet
elif query_complexity == "complex":
    model = "anthropic.claude-3-sonnet-20240229-v1:0"
```

### 2. Use Shorter Prompts

```python
# Bad - verbose prompt
prompt = "I would like you to please analyze the following document..."

# Good - concise prompt
prompt = "Analyze this document:"
```

### 3. Optimize Context Size

```python
# Retrieve fewer, more relevant documents
settings.retrieval_top_k = 3  # Instead of 10
settings.reranking_top_k = 2  # Instead of 5
```

### 4. Cache Embeddings

```python
# Embeddings are already cached in vector store
# Don't re-embed the same documents
```

### 5. Use Provisioned Throughput

For high-volume (>1M tokens/day), consider provisioned throughput:

```bash
# Can save up to 50% for consistent usage
aws bedrock create-provisioned-model-throughput \
    --model-id anthropic.claude-3-sonnet-20240229-v1:0 \
    --model-units 1
```

## 📈 Performance Optimization

### 1. Choose Nearby Region

```python
# Lower latency - same region as data
BEDROCK_REGION=us-east-1  # If S3 bucket is in us-east-1
```

### 2. Use Streaming for Long Responses

```python
from rag_ecosystem.components.generation import ResponseGenerator

generator = ResponseGenerator()
for chunk in generator.generate_streaming(query, documents):
    print(chunk, end='', flush=True)
```

### 3. Parallel Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Process multiple queries in parallel
with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(rag.query, queries)
```

## 🔍 Monitoring

### 1. CloudWatch Metrics

Bedrock automatically logs:
- `InvocationLatency` - Response time
- `InvocationErrors` - Error count
- `InputTokens` - Tokens sent
- `OutputTokens` - Tokens generated

### 2. Create Alarms

```bash
aws cloudwatch put-metric-alarm \
    --alarm-name bedrock-high-latency \
    --metric-name InvocationLatency \
    --namespace AWS/Bedrock \
    --statistic Average \
    --period 300 \
    --threshold 5000 \
    --comparison-operator GreaterThanThreshold
```

### 3. Cost Tracking

```bash
# View Bedrock costs
aws ce get-cost-and-usage \
    --time-period Start=2025-01-01,End=2025-01-31 \
    --granularity DAILY \
    --filter file://bedrock-filter.json \
    --metrics BlendedCost
```

## 🌍 Regional Availability

Bedrock is available in:
- **us-east-1** (N. Virginia) - Most models
- **us-west-2** (Oregon) - Most models
- **eu-west-1** (Ireland)
- **eu-central-1** (Frankfurt)
- **ap-northeast-1** (Tokyo)
- **ap-southeast-1** (Singapore)

**Recommendation**: Use `us-east-1` or `us-west-2` for full model access.

## 🐛 Troubleshooting

### Error: "Access Denied"

**Solution**: Request model access in Bedrock console

```bash
# Check model access status
aws bedrock list-foundation-models --region us-east-1
```

### Error: "Throttling Exception"

**Solution**: Request quota increase or use provisioned throughput

```bash
# Request quota increase
aws service-quotas request-service-quota-increase \
    --service-code bedrock \
    --quota-code L-12345678 \
    --desired-value 1000
```

### Error: "Model not found"

**Solution**: Check model ID and region

```bash
# List available models in your region
aws bedrock list-foundation-models --region us-east-1
```

### High Latency

**Causes:**
1. Cross-region calls
2. Large context size
3. Network issues

**Solutions:**
1. Use same region as your deployment
2. Reduce context size
3. Use VPC endpoints

## 📚 Additional Resources

- [Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)
- [Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Model Comparison](https://docs.anthropic.com/claude/docs/models-overview)
- [Best Practices](https://docs.aws.amazon.com/bedrock/latest/userguide/best-practices.html)

## 🎯 Next Steps

1. **Request model access** in Bedrock console
2. **Update IAM policies** with Bedrock permissions
3. **Configure .env** with Bedrock settings
4. **Test locally** before deploying
5. **Deploy to Lambda/EC2** with confidence

Bedrock makes your RAG system fully AWS-native, more secure, and potentially more cost-effective! 🚀
