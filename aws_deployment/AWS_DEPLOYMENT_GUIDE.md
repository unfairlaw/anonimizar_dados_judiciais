## AWS Deployment Guide for RAG Ecosystem

Complete guide for deploying the RAG system on AWS Lambda or EC2 with S3 integration.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [S3 Setup](#s3-setup)
4. [Lambda Deployment](#lambda-deployment)
5. [EC2 Deployment](#ec2-deployment)
6. [Cost Optimization](#cost-optimization)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
┌─────────────┐
│   S3 Bucket │
│             │
│  ┌────────┐ │
│  │ Docs/  │ │  ← Your documents
│  └────────┘ │
│             │
│  ┌────────┐ │
│  │Vector  │ │  ← Vector store (ChromaDB)
│  │Store/  │ │
│  └────────┘ │
└──────┬──────┘
       │
       ├────────────────┬──────────────────┐
       │                │                  │
       ▼                ▼                  ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Lambda    │  │     EC2     │  │    ECS      │
│  Serverless │  │   Instance  │  │  Container  │
└─────────────┘  └─────────────┘  └─────────────┘
```

---

## Prerequisites

### Required

- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Python 3.11+
- OpenAI or Anthropic API key

### Install AWS CLI

```bash
# MacOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure
aws configure
```

---

## S3 Setup

### 1. Create S3 Bucket

```bash
# Set your bucket name
export BUCKET_NAME="my-rag-ecosystem-bucket"
export AWS_REGION="us-east-1"

# Create bucket
aws s3 mb s3://$BUCKET_NAME --region $AWS_REGION

# Enable versioning (recommended)
aws s3api put-bucket-versioning \
    --bucket $BUCKET_NAME \
    --versioning-configuration Status=Enabled
```

### 2. Create Folder Structure

```bash
# Create folders
aws s3api put-object --bucket $BUCKET_NAME --key documents/
aws s3api put-object --bucket $BUCKET_NAME --key vector_store/
```

### 3. Upload Documents

```bash
# Upload your documents
aws s3 cp /local/path/to/docs/ s3://$BUCKET_NAME/documents/ --recursive

# Or upload specific files
aws s3 cp document.txt s3://$BUCKET_NAME/documents/document.txt
```

### 4. Set Bucket Policy (Optional)

```bash
# Create policy file
cat > bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowLambdaAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::YOUR-ACCOUNT-ID:role/YOUR-LAMBDA-ROLE"
      },
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::$BUCKET_NAME/*",
        "arn:aws:s3:::$BUCKET_NAME"
      ]
    }
  ]
}
EOF

# Apply policy
aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://bucket-policy.json
```

---

## Lambda Deployment

### Option A: Manual Deployment

#### 1. Create IAM Role

```bash
# Create trust policy
cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
    --role-name RAGLambdaExecutionRole \
    --assume-role-policy-document file://trust-policy.json

# Attach basic Lambda execution policy
aws iam attach-role-policy \
    --role-name RAGLambdaExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create S3 access policy
cat > s3-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::$BUCKET_NAME/*",
        "arn:aws:s3:::$BUCKET_NAME"
      ]
    }
  ]
}
EOF

# Attach S3 policy
aws iam put-role-policy \
    --role-name RAGLambdaExecutionRole \
    --policy-name S3Access \
    --policy-document file://s3-policy.json
```

#### 2. Create Lambda Layer (for dependencies)

```bash
# Create layer directory
mkdir -p python/lib/python3.11/site-packages

# Install dependencies
pip install \
    langchain \
    langchain-community \
    langchain-openai \
    chromadb \
    sentence-transformers \
    -t python/lib/python3.11/site-packages

# Create layer zip (max 50MB uncompressed)
zip -r rag-dependencies-layer.zip python

# Upload layer
aws lambda publish-layer-version \
    --layer-name rag-dependencies \
    --zip-file fileb://rag-dependencies-layer.zip \
    --compatible-runtimes python3.11
```

**Note**: If dependencies exceed Lambda's 250MB limit, use EFS or container images.

#### 3. Deploy Lambda Function

```bash
cd aws_deployment/lambda

# Make deployment script executable
chmod +x deploy.sh

# Set environment variables
export LAMBDA_FUNCTION_NAME="rag-ecosystem"
export AWS_REGION="us-east-1"
export LAMBDA_ROLE_ARN="arn:aws:iam::YOUR-ACCOUNT-ID:role/RAGLambdaExecutionRole"

# Deploy
./deploy.sh
```

#### 4. Configure Environment Variables

```bash
aws lambda update-function-configuration \
    --function-name rag-ecosystem \
    --environment Variables="{
        S3_BUCKET_NAME=$BUCKET_NAME,
        S3_VECTOR_STORE_PREFIX=vector_store,
        OPENAI_API_KEY=your-api-key-here,
        LLM_PROVIDER=openai,
        LLM_MODEL=gpt-4-turbo-preview
    }"
```

#### 5. Test Lambda Function

```bash
# Query test
aws lambda invoke \
    --function-name rag-ecosystem \
    --payload '{"action":"query","query":"What is machine learning?"}' \
    response.json

cat response.json

# Index test
aws lambda invoke \
    --function-name rag-ecosystem \
    --payload '{"action":"index","s3_prefix":"documents/","file_pattern":".txt"}' \
    response.json

cat response.json
```

### Option B: Using AWS SAM

```bash
# Install AWS SAM CLI
brew install aws-sam-cli  # MacOS
# or download from: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html

# Deploy
cd aws_deployment/lambda
sam build
sam deploy --guided
```

---

## EC2 Deployment

### 1. Launch EC2 Instance

```bash
# Using AWS CLI
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \  # Ubuntu 22.04 LTS
    --instance-type t3.large \
    --key-name your-key-pair \
    --security-group-ids sg-xxxxxxxx \
    --iam-instance-profile Name=RAGInstanceProfile \
    --user-data file://aws_deployment/ec2/user-data.sh
```

**Or use AWS Console:**
1. Go to EC2 Dashboard
2. Click "Launch Instance"
3. Select Ubuntu 22.04 LTS
4. Instance type: **t3.large** (minimum)
5. Configure IAM role with S3 access
6. Configure security group (allow port 80/443)

### 2. Connect and Setup

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@ec2-xx-xx-xx-xx.compute.amazonaws.com

# Clone repository
git clone <your-repo-url>
cd anonimizar_dados_judiciais

# Run setup script
cd aws_deployment/ec2
chmod +x setup.sh

# Set environment variables
export S3_BUCKET_NAME="your-bucket-name"
export OPENAI_API_KEY="your-api-key"

# Run setup
./setup.sh
```

### 3. Start API Server

```bash
# Activate virtual environment
source /opt/rag-ecosystem/venv/bin/activate

# Start with Gunicorn (production)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    aws_deployment.ec2.api_server:app

# Or use screen/tmux for persistent session
screen -S rag-api
gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    aws_deployment.ec2.api_server:app
# Detach: Ctrl+A, D
```

### 4. Setup Nginx (Reverse Proxy)

```bash
# Install Nginx
sudo apt-get install -y nginx

# Configure Nginx
sudo cat > /etc/nginx/sites-available/rag-api <<EOF
server {
    listen 80;
    server_name your-domain.com;  # or EC2 public DNS

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/rag-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Setup as System Service

```bash
# Create systemd service
sudo cat > /etc/systemd/system/rag-ecosystem.service <<EOF
[Unit]
Description=RAG Ecosystem API
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/opt/rag-ecosystem
Environment="PATH=/opt/rag-ecosystem/venv/bin"
ExecStart=/opt/rag-ecosystem/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 aws_deployment.ec2.api_server:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable rag-ecosystem
sudo systemctl start rag-ecosystem

# Check status
sudo systemctl status rag-ecosystem
```

### 6. Test API

```bash
# Health check
curl http://your-ec2-public-ip/health

# Query
curl -X POST http://your-ec2-public-ip/query \
    -H "Content-Type: application/json" \
    -d '{"query":"What is machine learning?","enable_self_correction":true}'

# Index documents
curl -X POST http://your-ec2-public-ip/index \
    -H "Content-Type: application/json" \
    -d '{"s3_prefix":"documents/","file_pattern":".txt"}'
```

---

## Cost Optimization

### Lambda Costs

| Component | Pricing | Tips |
|-----------|---------|------|
| **Invocations** | $0.20 per 1M requests | Use caching |
| **Compute** | $0.0000166667 per GB-second | Optimize memory |
| **Data Transfer** | $0.09/GB out | Keep data in same region |

**Cost Example**: 1000 queries/day, 30s each, 10GB RAM
- Compute: 1000 × 30s × 10GB × $0.0000166667 = $5/day
- Requests: 1000 × $0.0000002 = $0.0002/day
- **Total**: ~$150/month

### EC2 Costs

| Instance | vCPU | RAM | Cost (on-demand) | Cost (reserved 1yr) |
|----------|------|-----|------------------|---------------------|
| t3.large | 2 | 8GB | $0.0832/hr (~$60/mo) | ~$35/mo |
| t3.xlarge | 4 | 16GB | $0.1664/hr (~$120/mo) | ~$70/mo |
| c6i.2xlarge | 8 | 16GB | $0.34/hr (~$245/mo) | ~$145/mo |

**Recommendations**:
- Use **Spot Instances** (up to 90% discount)
- Use **Reserved Instances** for production (up to 60% discount)
- Use **Auto Scaling** to match demand

### S3 Costs

- **Storage**: $0.023/GB/month
- **Requests**: $0.0004 per 1000 GET requests
- **Data Transfer**: Free within same region

**Cost Example**: 100GB storage + 10K requests/day
- Storage: 100GB × $0.023 = $2.30/month
- Requests: 300K × $0.0004/1000 = $0.12/month
- **Total**: ~$2.50/month

---

## Monitoring

### CloudWatch Metrics

```bash
# Enable detailed monitoring
aws lambda put-function-concurrency \
    --function-name rag-ecosystem \
    --reserved-concurrent-executions 100

# Create CloudWatch alarm for errors
aws cloudwatch put-metric-alarm \
    --alarm-name rag-errors \
    --metric-name Errors \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 300 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1
```

### Application Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/rag-ecosystem --follow

# View EC2 logs
tail -f /opt/rag-ecosystem/logs/rag.log
```

---

## Troubleshooting

### Lambda Issues

**Problem**: Lambda timeout
```bash
# Increase timeout (max 15 min)
aws lambda update-function-configuration \
    --function-name rag-ecosystem \
    --timeout 900
```

**Problem**: Out of memory
```bash
# Increase memory (max 10GB)
aws lambda update-function-configuration \
    --function-name rag-ecosystem \
    --memory-size 10240
```

**Problem**: Package too large
- Use Lambda Layers for dependencies
- Or use Container Images (up to 10GB)

### EC2 Issues

**Problem**: Out of memory
```bash
# Check memory usage
free -h

# Add swap space
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**Problem**: Slow performance
- Upgrade instance type
- Use GPU instances for embeddings (p3.*)
- Enable SSD storage (gp3 EBS volumes)

### S3 Issues

**Problem**: Access denied
```bash
# Check IAM role permissions
aws iam get-role-policy \
    --role-name RAGLambdaExecutionRole \
    --policy-name S3Access

# Test S3 access
aws s3 ls s3://$BUCKET_NAME
```

---

## Security Best Practices

1. **Use IAM Roles** (not access keys) for EC2/Lambda
2. **Encrypt S3 bucket** with AWS KMS
3. **Use AWS Secrets Manager** for API keys
4. **Enable VPC** for private networking
5. **Use HTTPS** with ACM certificates
6. **Enable CloudTrail** for audit logging

---

## Next Steps

After deployment:

1. **Index your documents**:
   ```bash
   # Lambda
   aws lambda invoke --function-name rag-ecosystem \
       --payload '{"action":"index","s3_prefix":"documents/"}' out.json

   # EC2
   curl -X POST http://your-domain/index \
       -d '{"s3_prefix":"documents/"}'
   ```

2. **Test queries**:
   ```bash
   # Lambda
   aws lambda invoke --function-name rag-ecosystem \
       --payload '{"action":"query","query":"test"}' out.json

   # EC2
   curl -X POST http://your-domain/query \
       -d '{"query":"test"}'
   ```

3. **Monitor performance** in CloudWatch

4. **Set up CI/CD** for automatic deployments

---

## Support

For issues or questions:
- Check logs in CloudWatch or `/opt/rag-ecosystem/logs/`
- Review IAM permissions
- Verify S3 bucket access
- Check API key configuration

Good luck with your deployment! 🚀
