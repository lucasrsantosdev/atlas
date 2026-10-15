from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(frozen=True)
class CapabilityProvider:
    name: str
    capabilities: frozenset[str]
    metadata: dict[str, object] = field(default_factory=dict)
class CapabilityRegistry:
    def __init__(self) -> None: self._providers: dict[str, CapabilityProvider]={}
    def register(self, provider: CapabilityProvider) -> None: self._providers[provider.name]=provider
    def providers_for(self, capability: str) -> tuple[CapabilityProvider,...]:
        return tuple(p for p in self._providers.values() if capability in p.capabilities)
    def has(self, capability: str) -> bool: return bool(self.providers_for(capability))
