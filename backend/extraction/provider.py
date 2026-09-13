# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .models import LLMProviderResponse

class BaseLLMProvider(ABC):
    """
    Abstract interface for LLM Providers.
    Decouples prompt generation and extraction pipelines from specific LLM vendors (Gemini, Claude, OpenAI, or Mock).
    """

    def __init__(self):
        self.call_count: int = 0
        self.call_history: List[Dict[str, Any]] = []

    def reset_call_metrics(self) -> None:
        self.call_count = 0
        self.call_history = []

    def record_call(self, response: LLMProviderResponse) -> None:
        self.call_count += 1
        self.call_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": response.model_name,
            "latency_ms": response.latency_ms,
            "is_mock": getattr(response, "is_mock", False),
            "is_cached": getattr(response, "is_cached", False),
            "success": not bool(response.error),
            "error": response.error,
        })

    def get_call_metrics(self) -> Dict[str, Any]:
        return {
            "call_count": self.call_count,
            "call_history": list(self.call_history),
        }

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if provider credentials and network endpoints are configured."""
        pass

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.0,
        **kwargs: Any
    ) -> LLMProviderResponse:
        """
        Invokes the provider and requests structured JSON output adhering to json_schema if supported.
        """
        pass

