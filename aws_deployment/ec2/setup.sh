#!/bin/bash
# Setup RAG system on EC2 instance

set -e

echo "======================================"
echo "Setting up RAG System on EC2"
echo "======================================"

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.11
echo "Installing Python 3.11..."
sudo apt-get install -y python3.11 python3.11-venv python3-pip

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y \
    build-essential \
    git \
    curl \
    wget \
    nginx \
    supervisor

# Create application directory
APP_DIR="/opt/rag-ecosystem"
echo "Creating application directory: $APP_DIR"
sudo mkdir -p $APP_DIR
sudo chown -R ubuntu:ubuntu $APP_DIR
cd $APP_DIR

# Clone or copy application code
echo "Setting up application code..."
# If using git:
# git clone <your-repo-url> .

# Create virtual environment
echo "Creating virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Gunicorn for production
pip install gunicorn fastapi uvicorn

# Create necessary directories
mkdir -p logs data/vector_store

# Set environment variables
echo "Setting up environment..."
cat > .env <<EOF
# AWS Configuration
AWS_REGION=us-east-1
S3_BUCKET_NAME=${S3_BUCKET_NAME:-my-rag-bucket}
S3_VECTOR_STORE_PREFIX=vector_store

# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=${OPENAI_API_KEY}

# Vector Store
VECTOR_STORE_TYPE=chroma
VECTOR_STORE_PATH=/opt/rag-ecosystem/data/vector_store

# Logging
LOG_LEVEL=INFO
LOG_FILE=/opt/rag-ecosystem/logs/rag.log
EOF

echo ""
echo "======================================"
echo "Setup completed!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Start the service: sudo systemctl start rag-ecosystem"
echo "3. Enable on boot: sudo systemctl enable rag-ecosystem"
echo ""
