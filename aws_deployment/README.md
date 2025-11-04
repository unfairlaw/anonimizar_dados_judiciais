# AWS Deployment for RAG Ecosystem

This directory contains everything needed to deploy the RAG Ecosystem on AWS with **AWS Bedrock** (recommended) or other LLM providers.

## 🌟 AWS Bedrock (Recommended)

**Why Bedrock?**
- ✅ **Fully AWS-native** - No external API dependencies
- ✅ **Better security** - Data stays in your AWS account
- ✅ **IAM authentication** - No API keys to manage
- ✅ **Lower latency** - Same-region processing
- ✅ **Cost-effective** - Pay-per-use with volume discounts
- ✅ **Multiple models** - Claude, Llama, Titan, Cohere

See **[BEDROCK_GUIDE.md](./BEDROCK_GUIDE.md)** for complete Bedrock setup instructions.

## 🏗️ Deployment Options

### 1. **AWS Lambda** (Serverless) ⚡
- **Best for**: Sporadic usage, cost optimization, auto-scaling
- **Pros**: No server management, pay-per-use, scales automatically
- **Cons**: Cold starts (5-30s), 15min timeout, package size limits
- **Cost**: ~$5-150/month (usage-based)
- **See**: `lambda/` directory

### 2. **EC2** (Virtual Machine) 🖥️
- **Best for**: Consistent usage, predictable latency, full control
- **Pros**: Always warm, no timeouts, unlimited customization
- **Cons**: Pay for idle time, manual scaling setup
- **Cost**: ~$35-60/month (t3.large with reserved pricing)
- **See**: `ec2/` directory

## 📁 Directory Structure

```
aws_deployment/
├── lambda/
│   ├── lambda_handler.py    # Lambda function code
│   ├── requirements.txt      # Lambda dependencies
│   └── deploy.sh            # Deployment script
├── ec2/
│   ├── api_server.py        # FastAPI server
│   └── setup.sh             # EC2 setup script
├── iam_policies.json        # IAM roles with Bedrock permissions
├── BEDROCK_GUIDE.md         # Complete Bedrock setup guide
└── AWS_DEPLOYMENT_GUIDE.md  # General AWS deployment guide
```

## 🚀 Quick Start with Bedrock

### Prerequisites

```bash
# Install AWS CLI
aws configure

# Request Bedrock model access (one-time)
# Visit: https://console.aws.amazon.com/bedrock/
# Enable: Claude 3 Sonnet, Titan Embeddings

# Set environment variables
export S3_BUCKET_NAME="your-rag-bucket"
export AWS_REGION="us-east-1"
```

### Option 1: Deploy to Lambda

```bash
cd lambda

# Create IAM role with Bedrock permissions
aws iam create-role \
    --role-name RAGLambdaRole \
    --assume-role-policy-document file://../iam_policies.json

# Attach Bedrock policy
aws iam put-role-policy \
    --role-name RAGLambdaRole \
    --policy-name BedrockAccess \
    --policy-document file://../iam_policies.json

# Deploy
export LAMBDA_ROLE_ARN="arn:aws:iam::YOUR-ACCOUNT:role/RAGLambdaRole"
./deploy.sh

# Configure for Bedrock (no API keys needed!)
aws lambda update-function-configuration \
    --function-name rag-ecosystem \
    --environment Variables="{
        S3_BUCKET_NAME=$S3_BUCKET_NAME,
        LLM_PROVIDER=bedrock,
        BEDROCK_REGION=us-east-1,
        BEDROCK_LLM_MODEL=anthropic.claude-3-sonnet-20240229-v1:0,
        BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v1,
        EMBEDDING_PROVIDER=bedrock
    }"

# Test
aws lambda invoke \
    --function-name rag-ecosystem \
    --payload '{"action":"query","query":"test"}' \
    output.json
```

### Option 2: Deploy to EC2

```bash
# Launch EC2 instance with Bedrock-enabled IAM role
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t3.large \
    --key-name your-key \
    --iam-instance-profile Name=RAGInstanceProfile

# SSH and setup
ssh -i your-key.pem ubuntu@ec2-ip-address
cd /path/to/repo/aws_deployment/ec2

# Configure for Bedrock
cat > .env <<EOF
LLM_PROVIDER=bedrock
BEDROCK_REGION=us-east-1
BEDROCK_LLM_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v1
EMBEDDING_PROVIDER=bedrock
S3_BUCKET_NAME=$S3_BUCKET_NAME
EOF

# Setup and start
./setup.sh
gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    aws_deployment.ec2.api_server:app
```

## 📊 Cost Comparison

### Bedrock Pricing (per 1M tokens)

| Model | Input | Output | Best For |
|-------|-------|--------|----------|
| **Claude 3 Haiku** | $0.25 | $1.25 | Fast, cheap queries |
| **Claude 3 Sonnet** | $3.00 | $15.00 | Balanced (default) |
| **Titan Text** | $0.13 | $0.17 | Budget option |
| **Titan Embeddings** | $0.10 | - | Embeddings |

### Infrastructure Costs

| Deployment | Low Usage | Medium Usage | High Usage |
|-----------|-----------|--------------|------------|
| **Lambda** | ~$5/mo | ~$50/mo | ~$150/mo |
| **EC2 t3.large** | ~$60/mo | ~$60/mo | ~$60/mo |
| **EC2 Reserved** | ~$35/mo | ~$35/mo | ~$35/mo |
| **S3 Storage** | ~$2/mo | ~$5/mo | ~$10/mo |

**Recommendation**:
- < 1000 queries/day → Lambda + Bedrock
- 1000-10000 queries/day → EC2 Reserved + Bedrock
- > 10000 queries/day → EC2 with Auto-Scaling + Bedrock

## 🔐 Security Checklist

- [ ] Request Bedrock model access
- [ ] Create IAM roles with least privilege
- [ ] Enable S3 bucket versioning
- [ ] Configure VPC for private networking (optional)
- [ ] Enable CloudWatch logging
- [ ] Enable CloudTrail for audit logs
- [ ] Use S3 encryption at rest
- [ ] NO API keys needed with Bedrock! ✅

## 📖 Documentation

- **[BEDROCK_GUIDE.md](./BEDROCK_GUIDE.md)** - Complete Bedrock setup, models, pricing
- **[AWS_DEPLOYMENT_GUIDE.md](./AWS_DEPLOYMENT_GUIDE.md)** - Detailed Lambda/EC2 deployment
- **[iam_policies.json](./iam_policies.json)** - IAM policies with Bedrock permissions

## 🧪 Testing

### Lambda with Bedrock

```bash
# Index documents from S3
aws lambda invoke \
    --function-name rag-ecosystem \
    --payload '{"action":"index","s3_prefix":"documents/"}' \
    response.json

# Query
aws lambda invoke \
    --function-name rag-ecosystem \
    --payload '{"action":"query","query":"What is in my documents?"}' \
    response.json

cat response.json
```

### EC2 API with Bedrock

```bash
# Health check
curl http://your-ec2-ip:8000/health

# Index documents
curl -X POST http://your-ec2-ip:8000/index \
    -H "Content-Type: application/json" \
    -d '{"s3_prefix":"documents/"}'

# Query
curl -X POST http://your-ec2-ip:8000/query \
    -H "Content-Type: application/json" \
    -d '{"query":"What is in my documents?"}'
```

## 🎯 Architecture

```
┌─────────────────────────────────────────┐
│          S3 Bucket                      │
│  ├── documents/      (your files)       │
│  └── vector_store/   (embeddings)       │
└────────────────┬────────────────────────┘
                 │
                 ├──────────┐
                 ▼          ▼
         ┌──────────┐  ┌──────────┐
         │  Lambda  │  │   EC2    │
         └─────┬────┘  └─────┬────┘
               │             │
               └──────┬──────┘
                      ▼
         ┌────────────────────────┐
         │    AWS Bedrock         │
         │  ├── Claude 3 Sonnet   │
         │  └── Titan Embeddings  │
         └────────────────────────┘
```

## 💡 Tips

1. **Start with Bedrock** - No API keys, better security
2. **Use Claude 3 Haiku** for development - Faster & cheaper
3. **Use Claude 3 Sonnet** for production - Better quality
4. **Enable VPC endpoints** - Lower latency, better security
5. **Monitor costs** - Set CloudWatch billing alarms

## 🐛 Troubleshooting

**Error: "Access Denied to Bedrock"**
- Request model access in Bedrock console
- Check IAM role has `bedrock:InvokeModel` permission

**Error: "Model not found"**
- Verify model ID is correct for your region
- Check model is enabled in Bedrock console

**High latency**
- Use same AWS region for all resources
- Consider VPC endpoints for Bedrock

## 📞 Support

For deployment issues:
1. Check CloudWatch logs
2. Verify IAM permissions
3. Test Bedrock access with AWS CLI
4. Review [BEDROCK_GUIDE.md](./BEDROCK_GUIDE.md)

Ready to deploy with Bedrock! 🚀
