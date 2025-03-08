from dataclasses import dataclass


@dataclass(frozen=True)
class Model:
    model_id: str
    max_tokens: int | None
    temperature: float | None
