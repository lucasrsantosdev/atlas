"""Minimal pure behavior tree for explicit, side-effect-free predicates."""
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class Condition:
    predicate: Callable[[dict], bool]
    def evaluate(self, context: dict) -> bool: return bool(self.predicate(context))

@dataclass(frozen=True)
class All:
    children: tuple
    def evaluate(self, context: dict) -> bool: return all(x.evaluate(context) for x in self.children)

@dataclass(frozen=True)
class Any:
    children: tuple
    def evaluate(self, context: dict) -> bool: return any(x.evaluate(context) for x in self.children)
