#!/usr/bin/env python3
"""
Simple Bedrock API Example
Quick start script to test your Bedrock connection
"""

import boto3
import json


def simple_bedrock_call():
    """
    Simplest possible Bedrock API call
    """

    # Initialize Bedrock client
    client = boto3.client('bedrock-runtime', region_name='us-east-1')

    # Model ID for Claude 3.5 Sonnet
    model_id = 'anthropic.claude-3-5-sonnet-20241022-v2:0'

    # Your message
    messages = [
        {
            'role': 'user',
            'content': [
                {
                    'text': 'Olá! Em uma frase, explique o que você pode fazer.'
                }
            ]
        }
    ]

    # Call the API
    print("Calling Bedrock API...")
    response = client.converse(
        modelId=model_id,
        messages=messages,
        inferenceConfig={
            'maxTokens': 200,
            'temperature': 1.0
        }
    )

    # Extract the response
    output_message = response['output']['message']
    response_text = output_message['content'][0]['text']

    # Get token usage
    usage = response['usage']

    # Display results
    print("\n" + "="*60)
    print("RESPONSE:")
    print("="*60)
    print(response_text)
    print("\n" + "="*60)
    print("TOKEN USAGE:")
    print("="*60)
    print(f"Input tokens:  {usage['inputTokens']}")
    print(f"Output tokens: {usage['outputTokens']}")
    print(f"Total tokens:  {usage['totalTokens']}")
    print("="*60)


def main():
    try:
        simple_bedrock_call()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("  1. AWS credentials configured (run: aws configure)")
        print("  2. boto3 installed (run: pip install boto3)")
        print("  3. Access to Bedrock API in your AWS account")
        print("  4. Claude models enabled in Bedrock console")


if __name__ == "__main__":
    main()
