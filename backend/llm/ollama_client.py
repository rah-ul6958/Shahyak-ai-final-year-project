"""
SAHAYAK-AI Ollama Client

Local LLM inference using Ollama (never external APIs).
"""

from typing import Any, Dict, List, Optional

import httpx
import structlog

from config import settings

logger = structlog.get_logger(__name__)


class OllamaClient:
    """
    Ollama HTTP client for local LLM inference.
    """

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize Ollama client.

        Args:
            base_url: Ollama service base URL
        """
        self.base_url = base_url or settings.ollama_host

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to Ollama.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request arguments

        Returns:
            Response JSON

        Raises:
            httpx.HTTPError: If request fails
        """
        url = f"{self.base_url}/{endpoint}"

        logger.debug(
            "ollama_request",
            method=method,
            endpoint=endpoint,
            url=url,
        )

        with httpx.Client(timeout=120.0) as client:
            response = client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()

    def list(self) -> Dict[str, Any]:
        """
        List available models.

        Returns:
            List of available models
        """
        return self._request("GET", "api/tags")

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        format: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send chat completion request.

        Args:
            model: Model name
            messages: List of message dicts with role and content
            format: Response format (json for structured output)
            options: Model options (temperature, etc.)

        Returns:
            Chat response
        """
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
        }

        if format:
            payload["format"] = format

        if options:
            payload["options"] = options

        logger.info(
            "ollama_chat_request",
            model=model,
            message_count=len(messages),
            format=format,
        )

        return self._request("POST", "api/chat", json=payload)

    def generate(
        self,
        model: str,
        prompt: str,
        format: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send text generation request.

        Args:
            model: Model name
            prompt: Prompt text
            format: Response format
            options: Model options

        Returns:
            Generation response
        """
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
        }

        if format:
            payload["format"] = format

        if options:
            payload["options"] = options

        return self._request("POST", "api/generate", json=payload)

    async def chat_async(
        self,
        model: str,
        messages: List[Dict[str, str]],
        format: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Async version of chat request.

        Args:
            model: Model name
            messages: List of message dicts
            format: Response format
            options: Model options

        Returns:
            Chat response
        """
        url = f"{self.base_url}/api/chat"

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
        }

        if format:
            payload["format"] = format

        if options:
            payload["options"] = options

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

    def health_check(self) -> bool:
        """
        Check if Ollama service is reachable.

        Returns:
            True if Ollama is healthy
        """
        try:
            self.list()
            return True
        except Exception as e:
            logger.warning("ollama_health_check_failed", error=str(e))
            return False


# Global Ollama client instance
_ollama_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    """
    Get global Ollama client instance.

    Returns:
        OllamaClient instance
    """
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client