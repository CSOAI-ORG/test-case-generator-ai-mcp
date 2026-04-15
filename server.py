#!/usr/bin/env python3
"""Test case generation and coverage analysis — MEOK AI Labs."""
import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json
import re
import hashlib
from datetime import datetime, timezone
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)


def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now - t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT:
        return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now)
    return None


def _parse_signature(sig: str) -> dict:
    """Parse a function signature into name and parameters."""
    match = re.match(r'(?:def\s+)?(\w+)\s*\(([^)]*)\)', sig.strip())
    if not match:
        return {"name": sig.strip(), "params": []}
    name = match.group(1)
    raw_params = match.group(2)
    params = []
    for p in raw_params.split(","):
        p = p.strip()
        if not p:
            continue
        parts = p.split(":")
        pname = parts[0].strip().split("=")[0].strip()
        ptype = parts[1].strip().split("=")[0].strip() if len(parts) > 1 else "any"
        has_default = "=" in p
        params.append({"name": pname, "type": ptype, "has_default": has_default})
    return {"name": name, "params": params}


_TYPE_EXAMPLES = {
    "str": ["", "hello", "a" * 256, "hello world", "  spaces  ", "Special!@#$%"],
    "int": [0, 1, -1, 42, 2147483647, -2147483648],
    "float": [0.0, 1.0, -1.0, 3.14, float("inf"), -0.001],
    "bool": [True, False],
    "list": [[], [1], [1, 2, 3], [None], list(range(100))],
    "dict": [{}, {"key": "value"}, {"a": 1, "b": 2}],
    "any": [None, 0, "", [], {}, True, "test"],
}

_EDGE_PATTERNS = {
    "str": ["empty string", "very long string (10k+ chars)", "unicode/emoji", "null bytes", "SQL injection pattern", "HTML/script tags", "whitespace only"],
    "int": ["zero", "negative", "max int", "min int", "overflow boundary"],
    "float": ["zero", "negative", "infinity", "NaN", "very small (epsilon)", "very large"],
    "bool": ["truthy non-bool", "falsy non-bool", "None"],
    "list": ["empty list", "single element", "very large list", "nested lists", "mixed types", "None elements"],
    "dict": ["empty dict", "missing keys", "extra keys", "nested dicts", "non-string keys"],
    "any": ["None", "wrong type", "empty", "boundary values"],
}


mcp = FastMCP("test-case-generator-ai", instructions="Test case generation and coverage analysis by MEOK AI Labs.")


@mcp.tool()
def generate_test_cases(function_signature: str, num_cases: int = 5, api_key: str = "") -> dict:
    """Generate test cases for a function based on its signature and parameter types."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(api_key or "anon"):
        return err

    parsed = _parse_signature(function_signature)
    cases = []
    for i in range(min(num_cases, 20)):
        inputs = {}
        for param in parsed["params"]:
            examples = _TYPE_EXAMPLES.get(param["type"], _TYPE_EXAMPLES["any"])
            inputs[param["name"]] = examples[i % len(examples)]
        case_id = hashlib.md5(f"{parsed['name']}_{i}".encode()).hexdigest()[:8]
        cases.append({
            "id": f"TC-{case_id}",
            "description": f"Test {parsed['name']} with {'default' if i == 0 else 'variant'} inputs (case {i+1})",
            "inputs": inputs,
            "expected_behavior": "should_return_valid_result" if i < num_cases // 2 else "should_handle_gracefully",
            "category": "happy_path" if i < num_cases // 2 else "boundary",
        })

    return {
        "function": parsed["name"],
        "parameters": parsed["params"],
        "test_cases": cases,
        "total": len(cases),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@mcp.tool()
def generate_edge_cases(function_signature: str, api_key: str = "") -> dict:
    """Generate edge cases and boundary conditions for a function."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(api_key or "anon"):
        return err

    parsed = _parse_signature(function_signature)
    edge_cases = []

    for param in parsed["params"]:
        patterns = _EDGE_PATTERNS.get(param["type"], _EDGE_PATTERNS["any"])
        for pattern in patterns:
            edge_cases.append({
                "parameter": param["name"],
                "type": param["type"],
                "edge_condition": pattern,
                "risk": "high" if "overflow" in pattern or "injection" in pattern else "medium",
                "test_strategy": "assert_raises" if "overflow" in pattern or "injection" in pattern else "assert_handles",
            })

    # Cross-parameter edge cases
    if len(parsed["params"]) > 1:
        edge_cases.append({
            "parameter": "all",
            "type": "combination",
            "edge_condition": "all parameters at boundary values simultaneously",
            "risk": "high",
            "test_strategy": "assert_handles",
        })
        edge_cases.append({
            "parameter": "all",
            "type": "combination",
            "edge_condition": "all parameters None/empty",
            "risk": "medium",
            "test_strategy": "assert_raises",
        })

    return {
        "function": parsed["name"],
        "edge_cases": edge_cases,
        "total": len(edge_cases),
        "risk_summary": {
            "high": sum(1 for e in edge_cases if e["risk"] == "high"),
            "medium": sum(1 for e in edge_cases if e["risk"] == "medium"),
        },
    }


@mcp.tool()
def generate_test_matrix(function_signature: str, parameters_values: dict = None, api_key: str = "") -> dict:
    """Generate a combinatorial test matrix from parameter value sets."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(api_key or "anon"):
        return err

    parsed = _parse_signature(function_signature)

    if parameters_values is None:
        parameters_values = {}
        for param in parsed["params"]:
            examples = _TYPE_EXAMPLES.get(param["type"], _TYPE_EXAMPLES["any"])
            parameters_values[param["name"]] = examples[:3]

    param_names = list(parameters_values.keys())
    param_vals = [parameters_values[n] for n in param_names]

    # Pairwise combination (limited to avoid explosion)
    combinations = []
    if len(param_vals) == 0:
        combinations = [{}]
    elif len(param_vals) == 1:
        combinations = [{param_names[0]: v} for v in param_vals[0]]
    else:
        max_combos = 50
        count = 0
        def _combine(idx, current):
            nonlocal count
            if count >= max_combos:
                return
            if idx == len(param_names):
                combinations.append(dict(current))
                count += 1
                return
            for val in param_vals[idx]:
                current[param_names[idx]] = val
                _combine(idx + 1, current)
        _combine(0, {})

    matrix = []
    for i, combo in enumerate(combinations):
        matrix.append({
            "id": f"M-{i+1:03d}",
            "inputs": combo,
            "priority": "high" if i < len(combinations) // 3 else "medium" if i < 2 * len(combinations) // 3 else "low",
        })

    return {
        "function": parsed["name"],
        "matrix": matrix,
        "total_combinations": len(matrix),
        "parameters": param_names,
        "coverage_type": "pairwise" if len(param_names) > 2 else "exhaustive",
    }


@mcp.tool()
def assess_coverage(function_signature: str, existing_tests: list = None, api_key: str = "") -> dict:
    """Assess test coverage gaps for a function given existing test descriptions."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(api_key or "anon"):
        return err

    parsed = _parse_signature(function_signature)
    existing_tests = existing_tests or []

    categories = {
        "happy_path": {"covered": False, "keywords": ["valid", "normal", "basic", "simple", "success", "correct"]},
        "boundary": {"covered": False, "keywords": ["boundary", "edge", "limit", "max", "min", "zero"]},
        "error_handling": {"covered": False, "keywords": ["error", "invalid", "exception", "fail", "wrong", "bad", "raise"]},
        "null_empty": {"covered": False, "keywords": ["null", "none", "empty", "missing", "blank"]},
        "type_safety": {"covered": False, "keywords": ["type", "string", "int", "float", "bool", "cast", "convert"]},
        "performance": {"covered": False, "keywords": ["large", "performance", "slow", "timeout", "memory", "load"]},
    }

    existing_lower = [t.lower() for t in existing_tests]
    for cat_name, cat_info in categories.items():
        for test in existing_lower:
            if any(kw in test for kw in cat_info["keywords"]):
                cat_info["covered"] = True
                break

    covered = sum(1 for c in categories.values() if c["covered"])
    total = len(categories)
    gaps = [name for name, info in categories.items() if not info["covered"]]

    suggestions = []
    for gap in gaps:
        for param in parsed["params"]:
            suggestions.append(f"Add {gap} test for parameter '{param['name']}' ({param['type']})")

    return {
        "function": parsed["name"],
        "coverage_score": round(covered / total * 100, 1),
        "categories_covered": covered,
        "categories_total": total,
        "gaps": gaps,
        "existing_test_count": len(existing_tests),
        "suggestions": suggestions[:10],
        "coverage_by_category": {name: info["covered"] for name, info in categories.items()},
    }


if __name__ == "__main__":
    mcp.run()
