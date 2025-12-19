"""
Multi-Provider LLM Architecture for Binah-Σ

Supports multiple LLM providers with automatic failover:
- Mistral AI
- Google Gemini
- DeepSeek

Features:
- Provider abstraction
- Automatic failover
- Cost tracking
- Performance monitoring
"""

import os
import json
import asyncio
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.call_count = 0
        self.total_tokens = 0

    @abstractmethod
    async def complete(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
        """
        Generate completion from messages.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature

        Returns:
            str: Generated text content
        """
        pass

    def get_stats(self) -> dict:
        """Get usage statistics for this provider"""
        return {
            "provider": self.__class__.__name__,
            "model": self.model,
            "calls": self.call_count,
            "total_tokens": self.total_tokens
        }


class MistralProvider(LLMProvider):
    """Mistral AI provider"""

    def __init__(self, api_key: str = None, model: str = "mistral-large-latest"):
        from mistralai import Mistral

        api_key = api_key or os.getenv("MISTRAL_API_KEY")
        super().__init__(api_key, model)
        self.client = Mistral(api_key=self.api_key)

    async def complete(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
        loop = asyncio.get_event_loop()

        def _call():
            return self.client.chat.complete(
                model=self.model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"}
            )

        response = await loop.run_in_executor(None, _call)
        self.call_count += 1

        return response.choices[0].message.content


class GeminiProvider(LLMProvider):
    """Google Gemini provider"""

    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash"):
        import google.generativeai as genai

        # DEBUG: Log version to verify Render is using updated library
        print(f"========================================")
        print(f"DEBUG: GEMINI PROVIDER INITIALIZING")
        print(f"DEBUG: google-generativeai VERSION: {genai.__version__}")
        print(f"DEBUG: Model requested: {model}")
        print(f"========================================")

        api_key = api_key or os.getenv("GEMINI_API_KEY")
        super().__init__(api_key, model)

        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(
            model_name=self.model,
            generation_config={
                "temperature": 0.2,
                "response_mime_type": "application/json"
            }
        )

    async def complete(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
        loop = asyncio.get_event_loop()

        # Convert messages to Gemini format
        # Gemini expects a single prompt, so we concatenate
        prompt_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt_parts.append(f"SYSTEM INSTRUCTIONS:\n{content}\n")
            elif role == "user":
                prompt_parts.append(f"USER:\n{content}\n")

        full_prompt = "\n".join(prompt_parts)
        full_prompt += "\n\nIMPORTANT: You MUST respond with ONLY valid JSON. No markdown, no code blocks, just pure JSON."

        def _call():
            response = self.client.generate_content(full_prompt)

            # Check for blocked content
            if not response.candidates:
                raise ValueError("Gemini blocked the response due to safety filters")

            # Check if response has text
            if not hasattr(response, 'text') or not response.text:
                raise ValueError("Gemini returned empty response")

            return response

        response = await loop.run_in_executor(None, _call)
        self.call_count += 1

        # Clean the response text (remove markdown if present)
        text = response.text.strip()

        # Remove markdown code blocks if present
        if text.startswith('```json'):
            text = text[7:]  # Remove ```json
        if text.startswith('```'):
            text = text[3:]  # Remove ```
        if text.endswith('```'):
            text = text[:-3]  # Remove trailing ```

        text = text.strip()

        # Validate it's valid JSON
        try:
            json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Gemini returned invalid JSON: {e}. Response: {text[:200]}")

        return text


class DeepSeekProvider(LLMProvider):
    """DeepSeek provider (OpenAI-compatible API)"""

    def __init__(self, api_key: str = None, model: str = "deepseek-chat"):
        from openai import OpenAI

        api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        super().__init__(api_key, model)

        # DeepSeek uses OpenAI-compatible API
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )

    async def complete(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
        loop = asyncio.get_event_loop()

        def _call():
            return self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"}
            )

        response = await loop.run_in_executor(None, _call)
        self.call_count += 1

        if response.usage:
            self.total_tokens += response.usage.total_tokens

        return response.choices[0].message.content


class LLMOrchestrator:
    """
    Manages multiple LLM providers with failover and selection logic.
    """

    def __init__(self, primary_provider: str = "mistral"):
        """
        Initialize orchestrator with available providers.

        Args:
            primary_provider: Primary provider to use ("mistral", "gemini", or "deepseek")
        """
        self.providers = {}
        self.primary_provider_name = primary_provider
        self.fallback_order = []

        # Initialize available providers
        self._init_providers()

    def _init_providers(self):
        """Initialize all available providers based on API keys"""

        # Try to initialize Mistral
        if os.getenv("MISTRAL_API_KEY"):
            try:
                self.providers["mistral"] = MistralProvider()
                self.fallback_order.append("mistral")
            except Exception as e:
                print(f"Warning: Failed to initialize Mistral: {e}")

        # Try to initialize Gemini
        if os.getenv("GEMINI_API_KEY"):
            try:
                self.providers["gemini"] = GeminiProvider()
                self.fallback_order.append("gemini")
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini: {e}")

        # Try to initialize DeepSeek
        if os.getenv("DEEPSEEK_API_KEY"):
            try:
                self.providers["deepseek"] = DeepSeekProvider()
                self.fallback_order.append("deepseek")
            except Exception as e:
                print(f"Warning: Failed to initialize DeepSeek: {e}")

        if not self.providers:
            raise RuntimeError("No LLM providers available. Check your API keys.")

        # Set primary provider to first available if specified one not available
        if self.primary_provider_name not in self.providers:
            self.primary_provider_name = self.fallback_order[0]
            print(f"Primary provider not available, using {self.primary_provider_name}")

    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        provider: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Generate completion with automatic failover.

        Args:
            messages: Message list
            temperature: Sampling temperature
            provider: Specific provider to use (optional)

        Returns:
            tuple: (content, provider_used)
        """
        # Determine provider order
        if provider and provider in self.providers:
            provider_order = [provider]
        else:
            # Start with primary, then fallback
            provider_order = [self.primary_provider_name] + [
                p for p in self.fallback_order if p != self.primary_provider_name
            ]

        last_error = None

        # Try each provider in order
        for provider_name in provider_order:
            if provider_name not in self.providers:
                continue

            try:
                provider_instance = self.providers[provider_name]
                content = await provider_instance.complete(messages, temperature)
                return content, provider_name
            except Exception as e:
                last_error = e
                print(f"Provider {provider_name} failed: {e}, trying next...")
                continue

        # All providers failed
        raise RuntimeError(
            f"All LLM providers failed. Last error: {last_error}"
        )

    def get_stats(self) -> dict:
        """Get statistics for all providers"""
        return {
            name: provider.get_stats()
            for name, provider in self.providers.items()
        }

    def set_primary_provider(self, provider: str):
        """Change primary provider"""
        if provider in self.providers:
            self.primary_provider_name = provider
        else:
            raise ValueError(f"Provider {provider} not available")
