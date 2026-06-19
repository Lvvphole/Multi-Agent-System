"""schema_validator.py — Code validates model output before it touches state.

Non-deterministic model output is parsed and validated against a JSON schema
here. Invalid output is rejected (raises) and never enters the state store.
"""
from __future__ import annotations
import json
from jsonschema import Draft202012Validator


class SchemaError(Exception):
    pass


def validate(instance: dict, schema: dict) -> dict:
    errors = sorted(Draft202012Validator(schema).iter_errors(instance),
                    key=lambda e: list(e.path))
    if errors:
        msgs = "; ".join(f"{list(e.path)}: {e.message}" for e in errors)
        raise SchemaError(msgs)
    return instance


def parse_and_validate(raw: str, schema: dict) -> dict:
    try:
        inst = json.loads(raw)
    except json.JSONDecodeError as e:
        raise SchemaError(f"not valid JSON: {e}")
    return validate(inst, schema)
