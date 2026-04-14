#!/usr/bin/env python3

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("test-case-generator-ai-mcp")
@mcp.tool(name="generate_test_cases")
async def generate_test_cases(function_signature: str, num_cases: int = 3, api_key: str = "") -> str:
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    cases = [{"input": f"arg_{i}", "expected": f"result_{i}", "description": f"Test case {i+1} for {function_signature}"} for i in range(num_cases)]
    return {"function": function_signature, "cases": cases}
@mcp.tool(name="edge_case_finder")
async def edge_case_finder(function_signature: str, api_key: str = "") -> str:
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    return {"edge_cases": ["empty_input", "null_values", "max_length", "negative_numbers", "unicode_input"]}
    return {"edge_cases": ["empty_input", "null_values", "max_length", "negative_numbers", "unicode_input"]}
if __name__ == "__main__":
    mcp.run()
