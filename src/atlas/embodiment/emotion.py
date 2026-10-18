"""Conservative explicit affect cues, not psychological diagnosis."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Affect:
    label: str
    confidence: float

class EmotionInterpreter:
    CUES={'happy':('feliz','alegre','happy'), 'sad':('triste','sad'), 'concerned':('preocupado','worried')}
    def interpret(self, text: str) -> Affect:
        if not isinstance(text,str): raise TypeError("text required")
        words=set(text.lower().split())
        for label,cues in self.CUES.items():
            if words.intersection(cues): return Affect(label,0.6)
        return Affect('neutral',0.0)
