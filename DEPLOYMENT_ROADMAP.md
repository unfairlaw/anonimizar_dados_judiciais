# RAG Ecosystem - Review & Deployment Roadmap

A step-by-step guide to understand, review, and deploy the RAG ecosystem on AWS.

---

## 📋 Phase 1: Understanding the Architecture (30 minutes)

### Step 1.1: Read the Overview
**Priority: CRITICAL**

Start here to understand what you have:

1. **README.md** (main project root)
   - Overall features
   - Project structure
   - Quick start guide

2. **ARCHITECTURE.md**
   - System design
   - Component interactions
   - Data flow diagrams
   - Self-correction mechanisms

**What to look for:**
- ✅ Understand the 6 main components
- ✅ Understand how data flows through the system
- ✅ Note the self-correction loop

---

## 📋 Phase 2: Configuration Review (15 minutes)

### Step 2.1: Environment Configuration
**Files to check:**

1. **`.env.example`**
   ```bash
   # Review this file line by line
   cat .env.example
   ```

   **What to check:**
   - Default provider is `bedrock`
   - Available Bedrock models listed
   - S3 configuration placeholders
   - All configuration options explained

2. **`rag_ecosystem/config/settings.py`**
   ```bash
   # Review configuration class
   cat rag_ecosystem/config/settings.py
   ```

   **What to check:**
   - Default values make sense
   - Bedrock is default provider
   - All settings are documented

### Step 2.2: System Prompts
**File:** `rag_ecosystem/config/prompts.py`

**What to check:**
- Query rewriting prompts
- Document grading prompts
- Response evaluation prompts
- Hallucination detection prompts

**Action:** Just read, understand what each prompt does

---

## 📋 Phase 3: Core Components Review (45 minutes)

Review in this order (dependency order):

### Step 3.1: Foundation Components

1. **`rag_ecosystem/utils/llm_factory.py`** ⭐ START HERE
   ```bash
   cat rag_ecosystem/utils/llm_factory.py
   ```
   - Creates LLMs (Bedrock/OpenAI/Anthropic/Ollama)
   - Creates embeddings (Bedrock/HuggingFace/OpenAI)
   - **This is the key to provider switching**

2. **`rag_ecosystem/components/bedrock_llm.py`**
   - Bedrock LLM wrapper
   - Supports all Bedrock models
   - Handles different model families

3. **`rag_ecosystem/components/bedrock_embeddings.py`**
   - Bedrock embeddings wrapper
   - Titan and Cohere support

### Step 3.2: Core RAG Components

Review in this order:

1. **`rag_ecosystem/components/query_transformation.py`**
   - Query rewriting
   - Query decomposition
   - Ambiguity checking

2. **`rag_ecosystem/components/routing.py`**
   - Routes queries to correct data source
   - Decision logic

3. **`rag_ecosystem/components/indexing.py`**
   - Document chunking
   - Embedding generation
   - Vector store management

4. **`rag_ecosystem/components/retrieval.py`**
   - Vector search
   - Keyword search (BM25)
   - Hybrid search

5. **`rag_ecosystem/components/reranking.py`**
   - Cross-encoder reranking
   - Relevance filtering

6. **`rag_ecosystem/components/generation.py`**
   - Response generation
   - Context formatting

### Step 3.3: Agentic Components

1. **`rag_ecosystem/agents/document_grader.py`**
   - LLM-based document relevance grading

2. **`rag_ecosystem/agents/response_evaluator.py`**
   - Response quality evaluation
   - Hallucination detection

3. **`rag_ecosystem/agents/agentic_rag.py`** ⭐ MAIN ORCHESTRATOR
   - Combines all components
   - Self-correction loop
   - Multi-hop queries

**What to check:**
- ✅ Uses `create_llm()` and `create_embeddings()` from factory
- ✅ Error handling present
- ✅ Logging statements
- ✅ No hardcoded credentials

---

## 📋 Phase 4: AWS Integration Review (30 minutes)

### Step 4.1: S3 Integration Components

1. **`rag_ecosystem/components/s3_loader.py`**
   ```bash
   cat rag_ecosystem/components/s3_loader.py
   ```
   - Loads documents from S3
   - Lists files with filters
   - Uses boto3

   **What to check:**
   - ✅ Uses IAM roles (not hardcoded keys)
   - ✅ Error handling for S3 operations
   - ✅ Supports different file types

2. **`rag_ecosystem/components/s3_vector_store.py`**
   - Syncs vector store to/from S3
   - Upload/download operations

   **What to check:**
   - ✅ Local path is `/tmp/vector_store` (Lambda compatible)
   - ✅ Handles missing S3 data gracefully

### Step 4.2: Lambda Deployment

1. **`aws_deployment/lambda/lambda_handler.py`** ⭐ LAMBDA ENTRY POINT
   ```bash
   cat aws_deployment/lambda/lambda_handler.py
   ```

   **What to check:**
   - ✅ Three actions: query, index, stats
   - ✅ Global variables for warm starts
   - ✅ S3 vector store sync
   - ✅ Error handling and logging
   - ✅ No hardcoded credentials

2. **`aws_deployment/lambda/deploy.sh`**
   ```bash
   cat aws_deployment/lambda/deploy.sh
   ```

   **What to check:**
   - ✅ Creates deployment package
   - ✅ Sets timeout to 900s (15 min max)
   - ✅ Sets memory to 10GB (max)
   - ✅ Requires `LAMBDA_ROLE_ARN` env var

3. **`aws_deployment/lambda/requirements.txt`**
   - Lambda-specific dependencies
   - Note about Lambda layers

### Step 4.3: EC2 Deployment

1. **`aws_deployment/ec2/api_server.py`** ⭐ EC2 API SERVER
   ```bash
   cat aws_deployment/ec2/api_server.py
   ```

   **What to check:**
   - ✅ FastAPI application
   - ✅ Endpoints: /query, /index, /stats, /health
   - ✅ S3 sync on startup/shutdown
   - ✅ Error handling

2. **`aws_deployment/ec2/setup.sh`**
   ```bash
   cat aws_deployment/ec2/setup.sh
   ```

   **What to check:**
   - ✅ Installs system dependencies
   - ✅ Creates virtual environment
   - ✅ Sets up .env file
   - ✅ Creates directories

### Step 4.4: IAM Policies

**`aws_deployment/iam_policies.json`**
```bash
cat aws_deployment/iam_policies.json
```

**What to check:**
- ✅ Bedrock permissions: `bedrock:InvokeModel`
- ✅ S3 permissions: `s3:GetObject`, `s3:PutObject`, etc.
- ✅ CloudWatch logs permissions
- ✅ Separate policies for Lambda and EC2

---

## 📋 Phase 5: Documentation Review (20 minutes)

### Step 5.1: AWS Deployment Guides

1. **`aws_deployment/README.md`**
   - Quick start with Bedrock
   - Cost comparison
   - Architecture diagram

2. **`aws_deployment/BEDROCK_GUIDE.md`** ⭐ CRITICAL FOR BEDROCK
   - Why use Bedrock
   - Available models
   - Pricing details
   - Setup instructions
   - Cost optimization
   - Troubleshooting

3. **`aws_deployment/AWS_DEPLOYMENT_GUIDE.md`**
   - Detailed Lambda deployment
   - Detailed EC2 deployment
   - S3 setup
   - IAM configuration
   - Monitoring
   - Troubleshooting

**Action:** Read these to understand deployment options

---

## 📋 Phase 6: AWS Prerequisites Setup (30-60 minutes)

### Step 6.1: Request Bedrock Model Access
**MUST DO THIS FIRST**

```bash
# Option 1: AWS Console (easier)
# Visit: https://console.aws.amazon.com/bedrock/
# Click: "Model access" → Request access to:
#   - Anthropic Claude 3 Sonnet
#   - Anthropic Claude 3 Haiku
#   - Amazon Titan Embed Text

# Option 2: Check via CLI
aws bedrock list-foundation-models --region us-east-1
```

**Time to approval:** Usually instant, sometimes up to 24 hours

### Step 6.2: Create S3 Bucket

```bash
# Set variables
export S3_BUCKET_NAME="your-rag-ecosystem-bucket"
export AWS_REGION="us-east-1"

# Create bucket
aws s3 mb s3://$S3_BUCKET_NAME --region $AWS_REGION

# Enable versioning (recommended)
aws s3api put-bucket-versioning \
    --bucket $S3_BUCKET_NAME \
    --versioning-configuration Status=Enabled

# Create folder structure
aws s3api put-object --bucket $S3_BUCKET_NAME --key documents/
aws s3api put-object --bucket $S3_BUCKET_NAME --key vector_store/
```

### Step 6.3: Upload Test Documents

```bash
# Upload some test files
echo "Machine learning is a subset of AI." > test1.txt
echo "AWS Bedrock provides access to foundation models." > test2.txt

aws s3 cp test1.txt s3://$S3_BUCKET_NAME/documents/
aws s3 cp test2.txt s3://$S3_BUCKET_NAME/documents/

# Verify
aws s3 ls s3://$S3_BUCKET_NAME/documents/
```

### Step 6.4: Create IAM Role for Lambda

```bash
# Create trust policy file
cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
    --role-name RAGLambdaExecutionRole \
    --assume-role-policy-document file://trust-policy.json

# Attach managed policy for Lambda basics
aws iam attach-role-policy \
    --role-name RAGLambdaExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create custom policy for Bedrock + S3
cat > rag-policy.json <<EOF
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
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::$S3_BUCKET_NAME/*",
        "arn:aws:s3:::$S3_BUCKET_NAME"
      ]
    }
  ]
}
EOF

# Attach custom policy
aws iam put-role-policy \
    --role-name RAGLambdaExecutionRole \
    --policy-name RAGBedrockS3Access \
    --policy-document file://rag-policy.json

# Get role ARN (save this!)
aws iam get-role --role-name RAGLambdaExecutionRole --query 'Role.Arn' --output text
```

**Save the ARN output - you'll need it for deployment!**

---

## 📋 Phase 7: Local Testing (Optional, 30 minutes)

**Note:** You can skip this and go straight to AWS deployment if you prefer.

### Step 7.1: Install Dependencies Locally

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 7.2: Configure Local Environment

```bash
# Copy example env
cp .env.example .env

# Edit .env with your AWS credentials
nano .env  # or use your preferred editor
```

**Set these values:**
```bash
LLM_PROVIDER=bedrock
BEDROCK_REGION=us-east-1
BEDROCK_LLM_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v1
EMBEDDING_PROVIDER=bedrock

S3_BUCKET_NAME=your-bucket-name

# Only needed for local testing with AWS credentials
# (Not needed for Lambda/EC2 - they use IAM roles)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
```

### Step 7.3: Test Locally

```bash
# Test basic RAG
python -m rag_ecosystem.examples.basic_rag

# Test with S3
python -c "
from rag_ecosystem.components.s3_loader import S3DocumentLoader
from rag_ecosystem.agents.agentic_rag import AgenticRAG

# Load from S3
loader = S3DocumentLoader(bucket_name='$S3_BUCKET_NAME')
docs = loader.load_documents(prefix='documents/')
print(f'Loaded {len(docs)} documents from S3')

# Test query (will use Bedrock)
rag = AgenticRAG()
result = rag.query('What is machine learning?')
print(result['answer'])
"
```

---

## 📋 Phase 8: Lambda Deployment (30 minutes)

### Step 8.1: Deploy Lambda Function

```bash
cd aws_deployment/lambda

# Set environment variables
export LAMBDA_FUNCTION_NAME="rag-ecosystem"
export AWS_REGION="us-east-1"
export LAMBDA_ROLE_ARN="arn:aws:iam::YOUR-ACCOUNT-ID:role/RAGLambdaExecutionRole"

# Review deployment script first!
cat deploy.sh

# Make executable
chmod +x deploy.sh

# Deploy
./deploy.sh
```

**What happens:**
1. Creates deployment package
2. Zips code and dependencies
3. Creates or updates Lambda function
4. Sets timeout to 15 minutes
5. Sets memory to 10GB

### Step 8.2: Configure Lambda Environment

```bash
# Set environment variables
aws lambda update-function-configuration \
    --function-name rag-ecosystem \
    --environment Variables="{
        S3_BUCKET_NAME=$S3_BUCKET_NAME,
        LLM_PROVIDER=bedrock,
        BEDROCK_REGION=us-east-1,
        BEDROCK_LLM_MODEL=anthropic.claude-3-sonnet-20240229-v1:0,
        BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v1,
        EMBEDDING_PROVIDER=bedrock,
        EMBEDDING_MODEL=amazon.titan-embed-text-v1,
        EMBEDDING_DIMENSION=1536
    }" \
    --region $AWS_REGION
```

### Step 8.3: Test Lambda

```bash
# Test 1: Index documents from S3
aws lambda invoke \
    --function-name rag-ecosystem \
    --payload '{"action":"index","s3_prefix":"documents/","file_pattern":".txt"}' \
    --region $AWS_REGION \
    output.json

# Check output
cat output.json

# Test 2: Query
aws lambda invoke \
    --function-name rag-ecosystem \
    --payload '{"action":"query","query":"What is machine learning?"}' \
    --region $AWS_REGION \
    output.json

# Check output
cat output.json

# Test 3: Stats
aws lambda invoke \
    --function-name rag-ecosystem \
    --payload '{"action":"stats"}' \
    --region $AWS_REGION \
    output.json

cat output.json
```

---

## 📋 Phase 9: EC2 Deployment (Alternative to Lambda, 45 minutes)

**Only do this if you prefer EC2 over Lambda**

### Step 9.1: Launch EC2 Instance

```bash
# Create instance profile (one time)
aws iam create-instance-profile --instance-profile-name RAGInstanceProfile

aws iam add-role-to-instance-profile \
    --instance-profile-name RAGInstanceProfile \
    --role-name RAGLambdaExecutionRole  # Reuse same role

# Launch instance
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t3.large \
    --key-name YOUR-KEY-PAIR \
    --security-group-ids YOUR-SECURITY-GROUP \
    --iam-instance-profile Name=RAGInstanceProfile \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=RAG-Ecosystem}]'

# Get instance public IP
aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=RAG-Ecosystem" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text
```

### Step 9.2: SSH and Setup

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@INSTANCE-IP

# Clone repository
git clone YOUR-REPO-URL
cd anonimizar_dados_judiciais/aws_deployment/ec2

# Review setup script
cat setup.sh

# Set environment variables
export S3_BUCKET_NAME="your-bucket-name"

# Run setup
chmod +x setup.sh
./setup.sh
```

### Step 9.3: Start API Server

```bash
# Activate virtual environment
source /opt/rag-ecosystem/venv/bin/activate

# Start server
gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    aws_deployment.ec2.api_server:app
```

### Step 9.4: Test EC2 API

```bash
# From your local machine
export EC2_IP="your-ec2-public-ip"

# Health check
curl http://$EC2_IP:8000/health

# Index documents
curl -X POST http://$EC2_IP:8000/index \
    -H "Content-Type: application/json" \
    -d '{"s3_prefix":"documents/","file_pattern":".txt"}'

# Query
curl -X POST http://$EC2_IP:8000/query \
    -H "Content-Type: application/json" \
    -d '{"query":"What is machine learning?"}'

# Stats
curl http://$EC2_IP:8000/stats
```

---

## 📋 Phase 10: Validation & Monitoring (20 minutes)

### Step 10.1: CloudWatch Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/rag-ecosystem --follow

# View specific log group
aws logs describe-log-streams \
    --log-group-name /aws/lambda/rag-ecosystem \
    --order-by LastEventTime \
    --descending
```

### Step 10.2: Check Bedrock Usage

```bash
# CloudWatch metrics for Bedrock
aws cloudwatch get-metric-statistics \
    --namespace AWS/Bedrock \
    --metric-name InvocationCount \
    --start-time 2025-01-01T00:00:00Z \
    --end-time 2025-01-31T23:59:59Z \
    --period 86400 \
    --statistics Sum
```

### Step 10.3: Check S3 Contents

```bash
# List documents
aws s3 ls s3://$S3_BUCKET_NAME/documents/

# List vector store (should have files after indexing)
aws s3 ls s3://$S3_BUCKET_NAME/vector_store/ --recursive
```

### Step 10.4: Cost Estimation

```bash
# Check current month costs
aws ce get-cost-and-usage \
    --time-period Start=2025-01-01,End=2025-01-31 \
    --granularity MONTHLY \
    --metrics BlendedCost \
    --group-by Type=SERVICE
```

---

## 🎯 Quick Reference Checklist

### Pre-Deployment
- [ ] Bedrock model access requested and approved
- [ ] S3 bucket created with test documents
- [ ] IAM role created with Bedrock + S3 permissions
- [ ] Test documents uploaded to S3

### Lambda Deployment
- [ ] Reviewed lambda_handler.py
- [ ] Reviewed deploy.sh
- [ ] Deployed Lambda function
- [ ] Configured environment variables
- [ ] Tested index action
- [ ] Tested query action
- [ ] Checked CloudWatch logs

### EC2 Deployment (Alternative)
- [ ] Launched EC2 instance with IAM role
- [ ] Reviewed setup.sh
- [ ] Reviewed api_server.py
- [ ] Ran setup script
- [ ] Started API server
- [ ] Tested all endpoints
- [ ] Set up systemd service (optional)

### Validation
- [ ] CloudWatch logs show successful operations
- [ ] S3 vector store has files
- [ ] Queries return relevant answers
- [ ] No errors in logs
- [ ] Cost monitoring set up

---

## 🚨 Common Issues & Solutions

### Issue: "Access Denied" to Bedrock
**Solution:** Request model access in Bedrock console

### Issue: "Access Denied" to S3
**Solution:** Check IAM role has S3 permissions, bucket name is correct

### Issue: Lambda timeout
**Solution:** Already set to max (15 min), but check if documents are too large

### Issue: "Model not found"
**Solution:** Check region and model ID match available models

### Issue: High costs
**Solution:** Use Claude Haiku for development, monitor usage in CloudWatch

---

## 📞 Need Help?

1. **Check logs first:** CloudWatch logs for Lambda/EC2
2. **Review guides:**
   - `aws_deployment/BEDROCK_GUIDE.md` - Bedrock issues
   - `aws_deployment/AWS_DEPLOYMENT_GUIDE.md` - Deployment issues
3. **Test components individually:**
   - Test S3 access: `aws s3 ls s3://$S3_BUCKET_NAME`
   - Test Bedrock: Use AWS CLI or console
   - Test IAM: `aws iam get-role --role-name RAGLambdaExecutionRole`

---

## 🎉 Success Criteria

You're done when:
- ✅ Documents indexed from S3
- ✅ Queries return relevant answers
- ✅ No errors in CloudWatch logs
- ✅ Vector store synced to S3
- ✅ Costs are reasonable

**Estimated total time:** 3-4 hours for first deployment
**Estimated cost:** $5-20 for first month of testing

Ready to start! Follow this roadmap step by step. 🚀
