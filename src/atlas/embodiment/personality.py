"""Bounded, explicit personality settings; no hidden inference."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Personality:
    name: str = 'Atlas'
    expressiveness: float = 0.5
    def __post_init__(self):
        if not self.name or not isinstance(self.name,str): raise ValueError('name required')
        if isinstance(self.expressiveness,bool) or not isinstance(self.expressiveness,(float,int)) or not 0<=self.expressiveness<=1: raise ValueError('invalid expressiveness')
