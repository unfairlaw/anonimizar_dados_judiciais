# Bedrock Token Calculator Prototype

Simple scripts to estimate token counts for AWS Bedrock API calls.

## Files

- `bedrock_token_calculator.py` - Core calculator library
- `calculate_tokens.py` - Interactive CLI tool
- `TOKEN_CALCULATOR_README.md` - This file

## Quick Start

### Basic Usage

```bash
# Calculate tokens for text
python3 calculate_tokens.py 'Your text here'

# With cost estimation
python3 calculate_tokens.py --cost 'Your text here'

# From file
python3 calculate_tokens.py --file yourfile.txt

# From stdin
echo 'Your text' | python3 calculate_tokens.py --stdin
```

### Demo Script

```bash
# Run the demo to see examples
python3 bedrock_token_calculator.py
```

## Usage in Python Code

```python
from bedrock_token_calculator import BedrockTokenCalculator

# Initialize calculator
calculator = BedrockTokenCalculator(model_id='claude-3-5-sonnet')

# Estimate tokens for text
text = "Seu texto aqui"
tokens = calculator.estimate_tokens(text)
print(f"Estimated tokens: {tokens}")

# Calculate cost
cost_info = calculator.calculate_cost(
    input_tokens=1000,
    output_tokens=500
)
print(f"Total cost: ${cost_info['total_cost_usd']:.6f}")

# For chat messages
messages = [
    {"role": "user", "content": "Olá!"},
    {"role": "assistant", "content": "Como posso ajudar?"}
]
breakdown = calculator.estimate_message_tokens(messages)
print(f"Total tokens: {breakdown['total_tokens']}")
```

## Features

✅ Estimate tokens for text input
✅ Calculate tokens for chat message format
✅ Cost estimation for API calls
✅ Support for different Claude models
✅ Simple CLI interface

## Notes

- **These are ESTIMATES**: Actual token counts from Bedrock may vary
- Based on approximation of ~4 characters per token
- For exact counts, use Bedrock's actual token counting
- Default pricing is for Claude 3.5 Sonnet (as of 2024)

## Integration with Bedrock API

For more accurate token counting, you can use Bedrock's API:

```python
import boto3

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

# Count tokens using Bedrock API
response = bedrock.converse(
    modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
    messages=[{"role": "user", "content": [{"text": "Your text"}]}]
)

# Get actual token usage
usage = response['usage']
input_tokens = usage['inputTokens']
output_tokens = usage['outputTokens']
```

## Pricing Reference

| Model | Input (per 1k tokens) | Output (per 1k tokens) |
|-------|----------------------|------------------------|
| Claude 3.5 Sonnet | $0.003 | $0.015 |
| Claude 3 Opus | $0.015 | $0.075 |
| Claude 3 Sonnet | $0.003 | $0.015 |
| Claude 3 Haiku | $0.00025 | $0.00125 |

*Prices subject to change - check AWS pricing for current rates*

## Example Use Cases

### 1. Estimate cost before processing documents

```bash
python3 calculate_tokens.py --cost --file large_petition.txt
```

### 2. Calculate tokens for judicial data

```python
from bedrock_token_calculator import BedrockTokenCalculator
from anonimizar_dados_judiciais import generate_petition_data

calculator = BedrockTokenCalculator()
petition = generate_petition_data()

# Create petition text
text = f"""
Nome: {petition['namePF']}
CPF: {petition['cpf']}
Endereço: {petition['petition_addressaut']}
"""

tokens = calculator.estimate_tokens(text)
print(f"Petition will use ~{tokens} tokens")
```

### 3. Batch processing cost estimation

```python
calculator = BedrockTokenCalculator()

documents = ['doc1.txt', 'doc2.txt', 'doc3.txt']
total_tokens = 0

for doc_path in documents:
    with open(doc_path) as f:
        text = f.read()
    tokens = calculator.estimate_tokens(text)
    total_tokens += tokens

cost = calculator.calculate_cost(total_tokens, total_tokens * 0.5)
print(f"Batch processing estimated cost: ${cost['total_cost_usd']:.4f}")
```

## Future Enhancements

Ideas for improvement:

- [ ] Integration with boto3 for exact token counts
- [ ] Support for more Bedrock models
- [ ] Token usage tracking and reporting
- [ ] Batch file processing
- [ ] Configuration file for custom pricing
- [ ] Token optimization suggestions
- [ ] Real-time API integration

## License

This is a prototype script for development purposes.
