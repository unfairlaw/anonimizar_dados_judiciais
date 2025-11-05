#!/usr/bin/env python3
"""
Interactive Token Calculator for Bedrock
Quick tool to estimate tokens for text input
"""

import sys
from bedrock_token_calculator import BedrockTokenCalculator


def main():
    if len(sys.argv) < 2:
        print("Bedrock Token Calculator")
        print("=" * 60)
        print("\nUsage:")
        print("  python3 calculate_tokens.py 'Your text here'")
        print("  python3 calculate_tokens.py --file input.txt")
        print("  echo 'Your text' | python3 calculate_tokens.py --stdin")
        print("\nOptions:")
        print("  --model <model_id>  Specify model (default: claude-3-5-sonnet)")
        print("  --cost              Show cost estimate")
        print("  --file <path>       Read from file")
        print("  --stdin             Read from stdin")
        print("\nExamples:")
        print("  # Calculate tokens for text")
        print("  python3 calculate_tokens.py 'Olá mundo!'")
        print()
        print("  # From file")
        print("  python3 calculate_tokens.py --file petition.txt")
        print()
        print("  # With cost estimate")
        print("  python3 calculate_tokens.py --cost 'Your text here'")
        sys.exit(0)

    # Parse arguments
    model_id = 'claude-3-5-sonnet'
    show_cost = False
    text = None
    i = 1

    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg == '--model' and i + 1 < len(sys.argv):
            model_id = sys.argv[i + 1]
            i += 2
        elif arg == '--cost':
            show_cost = True
            i += 1
        elif arg == '--file' and i + 1 < len(sys.argv):
            with open(sys.argv[i + 1], 'r', encoding='utf-8') as f:
                text = f.read()
            i += 2
        elif arg == '--stdin':
            text = sys.stdin.read()
            i += 1
        else:
            # Treat as text input
            text = arg
            i += 1

    if not text:
        print("Error: No text provided")
        sys.exit(1)

    # Calculate tokens
    calculator = BedrockTokenCalculator(model_id=model_id)
    tokens = calculator.estimate_tokens(text)

    # Display results
    print(f"Model:           {model_id}")
    print(f"Text length:     {len(text)} characters")
    print(f"Estimated tokens: {tokens}")

    if show_cost:
        # Estimate with typical output token count
        estimated_output = int(tokens * 0.5)  # Assume response is 50% of input
        cost = calculator.calculate_cost(tokens, estimated_output)
        print()
        print("Cost Estimate:")
        print(f"  Input tokens:  {tokens}")
        print(f"  Output tokens: {estimated_output} (estimated)")
        print(f"  Total cost:    ${cost['total_cost_usd']:.6f}")

    print()
    print("(These are estimates - actual counts may vary)")


if __name__ == "__main__":
    main()
