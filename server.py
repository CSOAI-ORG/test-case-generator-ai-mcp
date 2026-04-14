#!/usr/bin/env python3
"""Generate test cases from function signatures. — MEOK AI Labs."""
import json, os, re, hashlib, uuid as _uuid, random
from datetime import datetime, timezone
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 30
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": "Limit/day"})
    _usage[c].append(now); return None

mcp = FastMCP("test-case-generator", instructions="MEOK AI Labs — Generate test cases from function signatures.")


@mcp.tool()
def generate_tests(function_signature: str, language: str = "python") -> str:
    """Generate test cases from a function signature."""
    if err := _rl(): return err
    name_match = re.search(r'def\s+(\w+)', function_signature)
    fname = name_match.group(1) if name_match else "my_function"
    tests = [
        f"def test_{fname}_basic():\n    result = {fname}()\n    assert result is not None",
        f"def test_{fname}_empty_input():\n    result = {fname}('')\n    assert result is not None",
        f"def test_{fname}_edge_case():\n    # Test boundary conditions\n    pass",
    ]
    return json.dumps({"function": fname, "tests": tests, "language": language, "count": len(tests)}, indent=2)

if __name__ == "__main__":
    mcp.run()
