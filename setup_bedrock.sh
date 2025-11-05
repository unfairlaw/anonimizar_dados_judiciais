#!/bin/bash
# Setup script for AWS Bedrock API Client

echo "=============================================="
echo "AWS Bedrock API Client - Setup"
echo "=============================================="
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 is installed"
echo ""

# Check if pip is installed
echo "🔍 Checking pip..."
python3 -m pip --version

if [ $? -ne 0 ]; then
    echo "❌ pip is not installed"
    exit 1
fi

echo "✓ pip is installed"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Check AWS CLI
echo "🔍 Checking AWS CLI..."
aws --version

if [ $? -ne 0 ]; then
    echo "⚠️  AWS CLI is not installed"
    echo "Install it from: https://aws.amazon.com/cli/"
    echo ""
else
    echo "✓ AWS CLI is installed"
    echo ""
fi

# Check AWS credentials
echo "🔍 Checking AWS credentials..."
aws sts get-caller-identity > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✓ AWS credentials are configured"
    echo ""
else
    echo "⚠️  AWS credentials not configured"
    echo "Run: aws configure"
    echo ""
fi

# Test bedrock access
echo "🧪 Testing Bedrock access..."
python3 bedrock_simple_example.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=============================================="
    echo "✓ Setup complete! Bedrock API is working."
    echo "=============================================="
    echo ""
    echo "Try these commands:"
    echo "  python3 bedrock_api_client.py interactive"
    echo "  python3 bedrock_api_client.py example1"
    echo "  python3 bedrock_api_client.py all"
else
    echo ""
    echo "=============================================="
    echo "⚠️  Setup complete but Bedrock test failed"
    echo "=============================================="
    echo ""
    echo "Possible issues:"
    echo "  1. AWS credentials not configured"
    echo "  2. No access to Bedrock API"
    echo "  3. Claude models not enabled"
    echo ""
    echo "Next steps:"
    echo "  1. Run: aws configure"
    echo "  2. Enable Bedrock in AWS Console"
    echo "  3. Request access to Claude models"
fi
