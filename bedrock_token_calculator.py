#!/usr/bin/env python3
"""
Bedrock Token Calculator Prototype
Simple script to estimate token counts for AWS Bedrock API calls
"""

import json
import sys


class BedrockTokenCalculator:
    """Calculate token estimates for AWS Bedrock models"""

    # Approximate tokens per character for different models
    # These are rough estimates; actual counts may vary
    MODEL_RATIOS = {
        'claude-3-sonnet': 0.25,      # ~4 chars per token
        'claude-3-haiku': 0.25,       # ~4 chars per token
        'claude-3-opus': 0.25,        # ~4 chars per token
        'claude-3-5-sonnet': 0.25,    # ~4 chars per token
        'anthropic.claude': 0.25,     # Generic Claude models
        'default': 0.25               # Default fallback
    }

    def __init__(self, model_id='claude-3-5-sonnet'):
        """Initialize calculator with a specific model ID"""
        self.model_id = model_id
        self.ratio = self._get_ratio(model_id)

    def _get_ratio(self, model_id):
        """Get the character-to-token ratio for a model"""
        for model_key, ratio in self.MODEL_RATIOS.items():
            if model_key in model_id.lower():
                return ratio
        return self.MODEL_RATIOS['default']

    def estimate_tokens(self, text):
        """
        Estimate token count for a given text

        Args:
            text (str): The text to estimate tokens for

        Returns:
            int: Estimated token count
        """
        if not text:
            return 0

        # Basic estimation: character count * ratio
        char_count = len(text)
        estimated_tokens = int(char_count * self.ratio)

        return estimated_tokens

    def estimate_message_tokens(self, messages):
        """
        Estimate tokens for a list of messages (chat format)

        Args:
            messages (list): List of message dicts with 'role' and 'content'

        Returns:
            dict: Token breakdown by message and total
        """
        breakdown = {
            'messages': [],
            'total_tokens': 0,
            'overhead_estimate': 0
        }

        for i, msg in enumerate(messages):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')

            # Estimate tokens for this message
            content_tokens = self.estimate_tokens(content)

            # Add overhead for role markers (~3-5 tokens per message)
            overhead = 4
            message_total = content_tokens + overhead

            breakdown['messages'].append({
                'index': i,
                'role': role,
                'content_tokens': content_tokens,
                'overhead': overhead,
                'total': message_total
            })

            breakdown['total_tokens'] += message_total

        # Add system overhead
        breakdown['overhead_estimate'] = len(messages) * 4

        return breakdown

    def calculate_cost(self, input_tokens, output_tokens, pricing=None):
        """
        Calculate estimated cost for API call

        Args:
            input_tokens (int): Number of input tokens
            output_tokens (int): Number of output tokens
            pricing (dict): Optional pricing info with 'input_per_1k' and 'output_per_1k'

        Returns:
            dict: Cost breakdown
        """
        # Default pricing for Claude 3.5 Sonnet (as of 2024)
        # Prices are per 1000 tokens
        if pricing is None:
            pricing = {
                'input_per_1k': 0.003,    # $0.003 per 1k input tokens
                'output_per_1k': 0.015    # $0.015 per 1k output tokens
            }

        input_cost = (input_tokens / 1000) * pricing['input_per_1k']
        output_cost = (output_tokens / 1000) * pricing['output_per_1k']
        total_cost = input_cost + output_cost

        return {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'input_cost_usd': round(input_cost, 6),
            'output_cost_usd': round(output_cost, 6),
            'total_cost_usd': round(total_cost, 6),
            'pricing': pricing
        }


def main():
    """Demo usage of the token calculator"""

    print("=" * 70)
    print("Bedrock Token Calculator - Prototype Demo")
    print("=" * 70)
    print()

    # Initialize calculator
    calculator = BedrockTokenCalculator(model_id='claude-3-5-sonnet')

    # Example 1: Simple text estimation
    print("Example 1: Simple Text Estimation")
    print("-" * 70)
    sample_text = "Olá, este é um texto de exemplo para calcular tokens na API Bedrock."
    tokens = calculator.estimate_tokens(sample_text)
    print(f"Text: {sample_text}")
    print(f"Estimated tokens: {tokens}")
    print()

    # Example 2: Chat messages
    print("Example 2: Chat Messages")
    print("-" * 70)
    messages = [
        {
            "role": "user",
            "content": "Qual é o processo judicial número 1234567-89.2023.1.00.0001?"
        },
        {
            "role": "assistant",
            "content": "O processo judicial que você mencionou está relacionado a um caso no tribunal. Posso ajudar com mais informações?"
        }
    ]

    breakdown = calculator.estimate_message_tokens(messages)
    print("Messages:")
    for msg_info in breakdown['messages']:
        print(f"  [{msg_info['role']}] {msg_info['content_tokens']} tokens (+ {msg_info['overhead']} overhead)")
    print(f"\nTotal estimated tokens: {breakdown['total_tokens']}")
    print()

    # Example 3: Cost calculation
    print("Example 3: Cost Estimation")
    print("-" * 70)
    input_tokens = 1000
    output_tokens = 500
    cost_info = calculator.calculate_cost(input_tokens, output_tokens)

    print(f"Input tokens:  {cost_info['input_tokens']:,}")
    print(f"Output tokens: {cost_info['output_tokens']:,}")
    print(f"Input cost:    ${cost_info['input_cost_usd']:.6f}")
    print(f"Output cost:   ${cost_info['output_cost_usd']:.6f}")
    print(f"Total cost:    ${cost_info['total_cost_usd']:.6f}")
    print()

    # Example 4: Large text from judicial data
    print("Example 4: Judicial Data Processing")
    print("-" * 70)
    judicial_text = f"""
    EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DA VARA CÍVEL

    Nome: João Silva
    CPF: 123.456.789-00
    RG: 12.345.678-9
    Endereço: Avenida Paulista, 1000, São Paulo - SP. CEP 01310-100

    Vem respeitosamente à presença de Vossa Excelência apresentar:

    AÇÃO DE INDENIZAÇÃO POR DANOS MORAIS

    Pelos fatos e fundamentos jurídicos a seguir expostos:

    1. DOS FATOS
    O autor foi vítima de danos causados pelo réu...
    """

    tokens = calculator.estimate_tokens(judicial_text)
    cost = calculator.calculate_cost(tokens, 200)  # Assume 200 token response

    print(f"Judicial text length: {len(judicial_text)} characters")
    print(f"Estimated input tokens: {tokens}")
    print(f"Estimated output tokens: 200")
    print(f"Estimated total cost: ${cost['total_cost_usd']:.6f}")
    print()

    print("=" * 70)
    print("Note: These are ESTIMATES. Actual token counts may vary.")
    print("For exact counts, use the Bedrock API's token counting feature.")
    print("=" * 70)


if __name__ == "__main__":
    main()
