#!/bin/bash
# Deploy RAG system to AWS Lambda

set -e

# Configuration
FUNCTION_NAME="${LAMBDA_FUNCTION_NAME:-rag-ecosystem}"
REGION="${AWS_REGION:-us-east-1}"
RUNTIME="python3.11"
TIMEOUT=900  # 15 minutes (max for Lambda)
MEMORY=10240  # 10GB (max for Lambda)
ROLE_ARN="${LAMBDA_ROLE_ARN}"

if [ -z "$ROLE_ARN" ]; then
    echo "Error: LAMBDA_ROLE_ARN environment variable required"
    exit 1
fi

echo "======================================"
echo "Deploying RAG System to AWS Lambda"
echo "======================================"
echo "Function: $FUNCTION_NAME"
echo "Region: $REGION"
echo "Runtime: $RUNTIME"
echo ""

# Create deployment package
echo "Creating deployment package..."
rm -rf package deployment.zip
mkdir -p package

# Copy application code
echo "Copying application code..."
cp -r ../../rag_ecosystem package/
cp lambda_handler.py package/

# Create ZIP
echo "Creating ZIP file..."
cd package
zip -r ../deployment.zip . -x "*.pyc" "__pycache__/*" "*.git/*"
cd ..

# Check size
SIZE=$(du -h deployment.zip | cut -f1)
echo "Deployment package size: $SIZE"

# Deploy to Lambda
echo ""
echo "Deploying to Lambda..."

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
    echo "Updating existing function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://deployment.zip \
        --region $REGION

    # Update configuration
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --timeout $TIMEOUT \
        --memory-size $MEMORY \
        --region $REGION
else
    echo "Creating new function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --role $ROLE_ARN \
        --handler lambda_handler.lambda_handler \
        --zip-file fileb://deployment.zip \
        --timeout $TIMEOUT \
        --memory-size $MEMORY \
        --region $REGION
fi

echo ""
echo "======================================"
echo "Deployment completed successfully!"
echo "======================================"
echo ""
echo "Test the function with:"
echo "aws lambda invoke --function-name $FUNCTION_NAME --payload '{\"action\":\"query\",\"query\":\"test\"}' output.json"
echo ""
