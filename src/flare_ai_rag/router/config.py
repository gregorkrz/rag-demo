from dataclasses import dataclass
from typing import Any

from flare_ai_rag.ai import Model
from flare_ai_rag.router.prompts import ROUTER_INSTRUCTION, ROUTER_PROMPT


@dataclass(frozen=True)
class RouterConfig:
    system_prompt: str
    router_prompt: str
    model: Model
    answer_option: str
    clarify_option: str
    reject_option: str

    @staticmethod
    def load(model_config: dict[str, Any]) -> "RouterConfig":
        """Loads the router config."""
        model = Model(
            model_id=model_config["id"],
            max_tokens=model_config.get("max_tokens"),
            temperature=model_config.get("temperature"),
        )

        return RouterConfig(
            system_prompt=ROUTER_INSTRUCTION,
            router_prompt=ROUTER_PROMPT,
            model=model,
            answer_option="ANSWER",
            clarify_option="CLARIFY",
            reject_option="REJECT",
        )
