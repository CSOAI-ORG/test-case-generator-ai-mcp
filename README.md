# Test Case Generator Ai

> By [MEOK AI Labs](https://meok.ai) — Test case generation and coverage analysis by MEOK AI Labs.

Test case generation and coverage analysis — MEOK AI Labs.

## Installation

```bash
pip install test-case-generator-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install test-case-generator-ai-mcp
```

## Tools

### `generate_test_cases`
Generate test cases for a function based on its signature and parameter types.

**Parameters:**
- `function_signature` (str)
- `num_cases` (int)

### `generate_edge_cases`
Generate edge cases and boundary conditions for a function.

**Parameters:**
- `function_signature` (str)

### `generate_test_matrix`
Generate a combinatorial test matrix from parameter value sets.

**Parameters:**
- `function_signature` (str)
- `parameters_values` (str)

### `assess_coverage`
Assess test coverage gaps for a function given existing test descriptions.

**Parameters:**
- `function_signature` (str)
- `existing_tests` (str)


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/test-case-generator-ai-mcp](https://github.com/CSOAI-ORG/test-case-generator-ai-mcp)
- **PyPI**: [pypi.org/project/test-case-generator-ai-mcp](https://pypi.org/project/test-case-generator-ai-mcp/)

## License

MIT — MEOK AI Labs
