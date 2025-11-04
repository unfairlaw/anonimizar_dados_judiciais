# AWS Deployment for RAG Ecosystem

This directory contains everything needed to deploy the RAG Ecosystem on AWS.

## 🏗️ Deployment Options

### 1. **AWS Lambda** (Serverless)
- **Best for**: Sporadic usage, cost optimization
- **Pros**: Auto-scaling, pay-per-use, no server management
- **Cons**: Cold starts (5-30s), 15min timeout, package size limits
- **See**: `lambda/` directory

### 2. **EC2** (Virtual Machine)
- **Best for**: Consistent usage, predictable latency
- **Pros**: No timeouts, full control, always warm
- **Cons**: Pay for idle time, manual scaling
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
├── iam_policies.json        # IAM roles and policies
└── AWS_DEPLOYMENT_GUIDE.md  # Complete deployment guide
```

## 🚀 Quick Start

### Prerequisites

```bash
# Install AWS CLI
aws configure

# Set environment variables
export S3_BUCKET_NAME="your-rag-bucket"
export OPENAI_API_KEY="your-api-key"
export AWS_REGION="us-east-1"
```

### Option 1: Deploy to Lambda

```bash
cd lambda

# Create IAM role (first time only)
aws iam create-role \
    --role-name RAGLambdaRole \
    --assume-role-policy-document file://../iam_policies.json

# Deploy
export LAMBDA_ROLE_ARN="arn:aws:iam::YOUR-ACCOUNT:role/RAGLambdaRole"
./deploy.sh

# Test
aws lambda invoke \
    --function-name rag-ecosystem \
    --payload '{"action":"query","query":"test"}' \
    output.json
```

### Option 2: Deploy to EC2

```bash
# Launch EC2 instance
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t3.large \
    --key-name your-key \
    --iam-instance-profile Name=RAGInstanceProfile

# SSH and setup
ssh -i your-key.pem ubuntu@ec2-ip-address
cd /path/to/repo/aws_deployment/ec2
./setup.sh

# Start API
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_server:app
```

## 📊 Cost Comparison

| Deployment | Low Usage | Medium Usage | High Usage |
|-----------|-----------|--------------|------------|
| **Lambda** | ~$5/mo | ~$50/mo | ~$150/mo |
| **EC2 t3.large** | ~$60/mo | ~$60/mo | ~$60/mo |
| **EC2 Reserved** | ~$35/mo | ~$35/mo | ~$35/mo |

**Recommendation**:
- < 1000 queries/day → Use Lambda
- 1000-10000 queries/day → Use EC2 with reserved instance
- > 10000 queries/day → Use EC2 with auto-scaling

## 🔐 Security Checklist

- [ ] Create S3 bucket with versioning enabled
- [ ] Setup IAM roles (no hardcoded credentials)
- [ ] Store API keys in AWS Secrets Manager
- [ ] Enable S3 encryption
- [ ] Configure VPC for private networking
- [ ] Setup CloudWatch alarms
- [ ] Enable CloudTrail logging

## 📖 Full Documentation

See [AWS_DEPLOYMENT_GUIDE.md](./AWS_DEPLOYMENT_GUIDE.md) for:
- Detailed setup instructions
- S3 configuration
- IAM policies
- Monitoring setup
- Troubleshooting
- Cost optimization tips

## 🧪 Testing

### Lambda

```bash
# Query
aws lambda invoke \
    --function-name rag-ecosystem \
    --payload '{"action":"query","query":"What is AI?"}' \
    response.json

# Index documents from S3
aws lambda invoke \
    --function-name rag-ecosystem \
    --payload '{"action":"index","s3_prefix":"documents/"}' \
    response.json
```

### EC2 API

```bash
# Health check
curl http://your-ec2-ip/health

# Query
curl -X POST http://your-ec2-ip/query \
    -H "Content-Type: application/json" \
    -d '{"query":"What is AI?"}'

# Index
curl -X POST http://your-ec2-ip/index \
    -H "Content-Type: application/json" \
    -d '{"s3_prefix":"documents/"}'
```

## 🎯 Architecture

```
User Request
     │
     ├─── Lambda ────┐
     │               │
     └─── EC2 ───────┤
                     │
                     ▼
              ┌──────────────┐
              │  S3 Bucket   │
              ├──────────────┤
              │ documents/   │  ← Your files
              │ vector_store/│  ← Embeddings
              └──────────────┘
```

## 📞 Support

Issues? Check:
1. CloudWatch logs for errors
2. IAM permissions
3. S3 bucket access
4. API key configuration

For detailed troubleshooting, see the [full guide](./AWS_DEPLOYMENT_GUIDE.md#troubleshooting).
