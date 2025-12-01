from __future__ import annotations

from typing import Any, Dict, Iterable


class JsonLogicEvaluator:
    """Lightweight evaluator supporting a subset of JSON-logic operators used by this project."""

    def __init__(self, context: Dict[str, Any]):
        self.context = context

    def evaluate(self, expr: Any) -> Any:
        if isinstance(expr, (int, float, str, bool)) or expr is None:
            return expr
        if isinstance(expr, list):
            return [self.evaluate(item) for item in expr]
        if isinstance(expr, dict):
            if len(expr) != 1:
                raise ValueError(f"Invalid expression {expr}")
            op, value = next(iter(expr.items()))
            method = getattr(self, f"op_{op}", None)
            if not method:
                raise ValueError(f"Unsupported operator {op}")
            return method(value)
        raise ValueError(f"Unsupported expression type: {type(expr)}")

    def op_var(self, key: str) -> Any:
        return self.context.get(key)

    def op_and(self, args: Iterable[Any]) -> bool:
        return all(self.evaluate(arg) for arg in args)

    def op_or(self, args: Iterable[Any]) -> bool:
        return any(self.evaluate(arg) for arg in args)

    def op_not(self, arg: Any) -> bool:
        return not self.evaluate(arg)

    def op_in(self, args: Iterable[Any]) -> bool:
        haystack, needle = list(args)
        evaluated_haystack = self.evaluate(haystack)
        evaluated_needle = self.evaluate(needle)
        return evaluated_haystack is not None and evaluated_needle in evaluated_haystack

    def op_eq(self, args: Iterable[Any]) -> bool:
        a, b = list(args)
        return self.evaluate(a) == self.evaluate(b)

    def op_neq(self, args: Iterable[Any]) -> bool:
        a, b = list(args)
        return self.evaluate(a) != self.evaluate(b)

    def op_gt(self, args: Iterable[Any]) -> bool:
        a, b = list(args)
        return self.evaluate(a) > self.evaluate(b)

    def op_gte(self, args: Iterable[Any]) -> bool:
        a, b = list(args)
        return self.evaluate(a) >= self.evaluate(b)

    def op_lt(self, args: Iterable[Any]) -> bool:
        a, b = list(args)
        return self.evaluate(a) < self.evaluate(b)

    def op_lte(self, args: Iterable[Any]) -> bool:
        a, b = list(args)
        return self.evaluate(a) <= self.evaluate(b)

