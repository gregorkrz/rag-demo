from dataclasses import dataclass
from typing import Any

from flare_ai_rag.ai import Model
from flare_ai_rag.responder.prompts import RESPONDER_INSTRUCTION, RESPONDER_PROMPT


@dataclass(frozen=True)
class ResponderConfig:
    model: Model
    system_prompt: str
    query_prompt: str

    @staticmethod
    def load(model_config: dict[str, Any]) -> "ResponderConfig":
        """Loads the Responder config."""
        model = Model(
            model_id=model_config["id"],
            max_tokens=model_config.get("max_tokens"),
            temperature=model_config.get("temperature"),
        )

        return ResponderConfig(
            model=model,
            system_prompt=RESPONDER_INSTRUCTION,
            query_prompt=RESPONDER_PROMPT,
        )
