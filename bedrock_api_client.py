#!/usr/bin/env python3
"""
AWS Bedrock API Client
Script to interact with Claude models via AWS Bedrock API
"""

import json
import sys
import os
from datetime import datetime

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    print("Error: boto3 is not installed.")
    print("Install with: pip install boto3")
    sys.exit(1)

# Import our token calculator
try:
    from bedrock_token_calculator import BedrockTokenCalculator
except ImportError:
    BedrockTokenCalculator = None


class BedrockClient:
    """Client for interacting with AWS Bedrock API"""

    # Available Claude models on Bedrock
    MODELS = {
        'claude-3-5-sonnet': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
        'claude-3-5-sonnet-v1': 'anthropic.claude-3-5-sonnet-20240620-v1:0',
        'claude-3-sonnet': 'anthropic.claude-3-sonnet-20240229-v1:0',
        'claude-3-haiku': 'anthropic.claude-3-haiku-20240307-v1:0',
        'claude-3-opus': 'anthropic.claude-3-opus-20240229-v1:0',
    }

    def __init__(self, region_name='us-east-1', model_id='claude-3-5-sonnet'):
        """
        Initialize Bedrock client

        Args:
            region_name (str): AWS region
            model_id (str): Model identifier (short name or full ARN)
        """
        self.region_name = region_name
        self.model_id = self._resolve_model_id(model_id)

        try:
            self.client = boto3.client(
                service_name='bedrock-runtime',
                region_name=region_name
            )
            print(f"✓ Connected to Bedrock in region: {region_name}")
            print(f"✓ Using model: {self.model_id}")
        except NoCredentialsError:
            print("Error: AWS credentials not found.")
            print("Configure with: aws configure")
            sys.exit(1)
        except Exception as e:
            print(f"Error initializing Bedrock client: {e}")
            sys.exit(1)

        # Initialize token calculator if available
        self.token_calculator = None
        if BedrockTokenCalculator:
            self.token_calculator = BedrockTokenCalculator(model_id=model_id)

    def _resolve_model_id(self, model_id):
        """Resolve short model name to full Bedrock model ID"""
        if model_id in self.MODELS:
            return self.MODELS[model_id]
        return model_id  # Already a full ID

    def invoke(self, messages, max_tokens=4096, temperature=1.0, system=None):
        """
        Invoke Claude model via Bedrock Converse API

        Args:
            messages (list): List of message dicts with 'role' and 'content'
            max_tokens (int): Maximum tokens to generate
            temperature (float): Temperature for sampling (0-1)
            system (str): Optional system prompt

        Returns:
            dict: Response with content, usage stats, and metadata
        """
        try:
            # Prepare request
            request_params = {
                'modelId': self.model_id,
                'messages': self._format_messages(messages),
                'inferenceConfig': {
                    'maxTokens': max_tokens,
                    'temperature': temperature,
                }
            }

            if system:
                request_params['system'] = [{'text': system}]

            # Estimate tokens before calling
            if self.token_calculator:
                estimated_tokens = self._estimate_input_tokens(messages, system)
                print(f"\n📊 Estimated input tokens: {estimated_tokens}")

            # Make API call
            print(f"🚀 Calling Bedrock API...")
            response = self.client.converse(**request_params)

            # Extract results
            result = self._parse_response(response)

            # Display token usage
            self._display_usage(result['usage'])

            return result

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            print(f"❌ Bedrock API Error [{error_code}]: {error_message}")
            raise
        except Exception as e:
            print(f"❌ Error: {e}")
            raise

    def invoke_stream(self, messages, max_tokens=4096, temperature=1.0, system=None):
        """
        Invoke Claude model with streaming response

        Args:
            messages (list): List of message dicts
            max_tokens (int): Maximum tokens to generate
            temperature (float): Temperature for sampling
            system (str): Optional system prompt

        Yields:
            str: Chunks of generated text
        """
        try:
            request_params = {
                'modelId': self.model_id,
                'messages': self._format_messages(messages),
                'inferenceConfig': {
                    'maxTokens': max_tokens,
                    'temperature': temperature,
                }
            }

            if system:
                request_params['system'] = [{'text': system}]

            print(f"🚀 Streaming from Bedrock API...\n")

            response = self.client.converse_stream(**request_params)
            stream = response.get('stream')

            if stream:
                for event in stream:
                    if 'contentBlockDelta' in event:
                        delta = event['contentBlockDelta']['delta']
                        if 'text' in delta:
                            chunk = delta['text']
                            yield chunk
                    elif 'metadata' in event:
                        # Final metadata with usage stats
                        metadata = event['metadata']
                        if 'usage' in metadata:
                            print("\n")
                            self._display_usage(metadata['usage'])

        except Exception as e:
            print(f"❌ Streaming error: {e}")
            raise

    def _format_messages(self, messages):
        """Format messages for Bedrock Converse API"""
        formatted = []
        for msg in messages:
            formatted.append({
                'role': msg['role'],
                'content': [{'text': msg['content']}]
            })
        return formatted

    def _parse_response(self, response):
        """Parse Bedrock API response"""
        output = response.get('output', {})
        message = output.get('message', {})
        content = message.get('content', [])

        # Extract text from content
        text = ''
        if content and len(content) > 0:
            text = content[0].get('text', '')

        return {
            'content': text,
            'role': message.get('role', 'assistant'),
            'usage': response.get('usage', {}),
            'stop_reason': response.get('stopReason', 'unknown'),
            'metrics': response.get('metrics', {})
        }

    def _estimate_input_tokens(self, messages, system=None):
        """Estimate input tokens using our calculator"""
        if not self.token_calculator:
            return 0

        breakdown = self.token_calculator.estimate_message_tokens(messages)
        total = breakdown['total_tokens']

        if system:
            total += self.token_calculator.estimate_tokens(system)

        return total

    def _display_usage(self, usage):
        """Display token usage and cost"""
        input_tokens = usage.get('inputTokens', 0)
        output_tokens = usage.get('outputTokens', 0)
        total_tokens = usage.get('totalTokens', 0)

        print(f"\n📈 Token Usage:")
        print(f"   Input:  {input_tokens:,} tokens")
        print(f"   Output: {output_tokens:,} tokens")
        print(f"   Total:  {total_tokens:,} tokens")

        # Calculate cost if we have the calculator
        if self.token_calculator:
            cost = self.token_calculator.calculate_cost(input_tokens, output_tokens)
            print(f"   Cost:   ${cost['total_cost_usd']:.6f}")


def example_simple_query():
    """Example 1: Simple question-answer"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Simple Query")
    print("="*70)

    client = BedrockClient(model_id='claude-3-5-sonnet')

    messages = [
        {
            'role': 'user',
            'content': 'Explique em uma frase o que é a Lei Geral de Proteção de Dados (LGPD).'
        }
    ]

    result = client.invoke(messages, max_tokens=200)

    print("\n💬 Response:")
    print(result['content'])


def example_judicial_data():
    """Example 2: Process judicial data"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Judicial Data Processing")
    print("="*70)

    try:
        from anonimizar_dados_judiciais import generate_petition_data
        petition = generate_petition_data()
    except ImportError:
        print("⚠️  Could not import petition generator")
        return

    client = BedrockClient(model_id='claude-3-haiku')  # Using Haiku for cost efficiency

    judicial_text = f"""
    Dados do Processo:
    - Nome: {petition['namePF']}
    - CPF: {petition['cpf']}
    - Endereço: {petition['petition_addressaut']}
    - Processo: {petition['judicialprocess']}
    """

    messages = [
        {
            'role': 'user',
            'content': f'Analise se os seguintes dados judiciais estão formatados corretamente:\n{judicial_text}'
        }
    ]

    result = client.invoke(messages, max_tokens=300)

    print("\n💬 Response:")
    print(result['content'])


def example_streaming():
    """Example 3: Streaming response"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Streaming Response")
    print("="*70)

    client = BedrockClient(model_id='claude-3-5-sonnet')

    messages = [
        {
            'role': 'user',
            'content': 'Liste 5 princípios importantes do direito processual civil brasileiro.'
        }
    ]

    print("\n💬 Response (streaming):")
    for chunk in client.invoke_stream(messages, max_tokens=500):
        print(chunk, end='', flush=True)
    print()


def example_conversation():
    """Example 4: Multi-turn conversation"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Multi-turn Conversation")
    print("="*70)

    client = BedrockClient(model_id='claude-3-5-sonnet')

    messages = [
        {
            'role': 'user',
            'content': 'O que é um processo judicial?'
        },
        {
            'role': 'assistant',
            'content': 'Um processo judicial é um procedimento formal conduzido perante um tribunal ou autoridade judicial para resolver disputas legais entre partes.'
        },
        {
            'role': 'user',
            'content': 'Quais são as principais fases?'
        }
    ]

    result = client.invoke(messages, max_tokens=400)

    print("\n💬 Response:")
    print(result['content'])


def example_with_system_prompt():
    """Example 5: Using system prompt"""
    print("\n" + "="*70)
    print("EXAMPLE 5: With System Prompt")
    print("="*70)

    client = BedrockClient(model_id='claude-3-5-sonnet')

    system = "Você é um assistente especializado em direito brasileiro. Responda de forma técnica e precisa."

    messages = [
        {
            'role': 'user',
            'content': 'O que é competência territorial?'
        }
    ]

    result = client.invoke(messages, max_tokens=300, system=system, temperature=0.7)

    print("\n💬 Response:")
    print(result['content'])


def interactive_mode():
    """Interactive chat mode"""
    print("\n" + "="*70)
    print("INTERACTIVE MODE")
    print("="*70)
    print("Type your questions (or 'exit' to quit)")

    client = BedrockClient(model_id='claude-3-5-sonnet')
    messages = []

    while True:
        try:
            user_input = input("\n👤 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit', 'sair']:
                print("Goodbye! 👋")
                break

            messages.append({
                'role': 'user',
                'content': user_input
            })

            result = client.invoke(messages, max_tokens=2000)

            print(f"\n🤖 Assistant:")
            print(result['content'])

            # Add assistant response to conversation
            messages.append({
                'role': 'assistant',
                'content': result['content']
            })

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            break


def main():
    """Main function with example selector"""

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'interactive':
            interactive_mode()
        elif command == 'example1':
            example_simple_query()
        elif command == 'example2':
            example_judicial_data()
        elif command == 'example3':
            example_streaming()
        elif command == 'example4':
            example_conversation()
        elif command == 'example5':
            example_with_system_prompt()
        elif command == 'all':
            example_simple_query()
            example_judicial_data()
            example_streaming()
            example_conversation()
            example_with_system_prompt()
        else:
            print(f"Unknown command: {command}")
            print_usage()
    else:
        print_usage()


def print_usage():
    """Print usage information"""
    print("AWS Bedrock API Client")
    print("=" * 70)
    print("\nUsage:")
    print("  python3 bedrock_api_client.py <command>")
    print("\nCommands:")
    print("  interactive  - Start interactive chat mode")
    print("  example1     - Simple query example")
    print("  example2     - Judicial data processing")
    print("  example3     - Streaming response")
    print("  example4     - Multi-turn conversation")
    print("  example5     - With system prompt")
    print("  all          - Run all examples")
    print("\nRequirements:")
    print("  - AWS credentials configured (aws configure)")
    print("  - boto3 installed (pip install boto3)")
    print("  - Access to Bedrock API in your AWS account")
    print("\nEnvironment Variables:")
    print("  AWS_REGION         - AWS region (default: us-east-1)")
    print("  AWS_PROFILE        - AWS profile to use")
    print("\nExamples:")
    print("  python3 bedrock_api_client.py interactive")
    print("  python3 bedrock_api_client.py example1")
    print("  python3 bedrock_api_client.py all")


if __name__ == "__main__":
    main()
