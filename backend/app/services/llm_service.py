import re

import requests

from app.core.config import Settings, get_settings


class LLMService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def generate(self, system_prompt: str, user_prompt: str, fallback: str) -> str:
        provider = self.settings.default_llm_provider.lower()
        try:
            if provider == "groq":
                return self._clean_output(self._call_groq(system_prompt, user_prompt))
            if provider == "openrouter":
                return self._clean_output(self._call_openrouter(system_prompt, user_prompt))
            if provider == "together":
                return self._clean_output(self._call_together(system_prompt, user_prompt))
        except requests.RequestException:
            return fallback
        return fallback

    def _messages(self, system_prompt: str, user_prompt: str) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _parse_chat_response(self, response: requests.Response) -> str:
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"].strip()
        return content

    def _call_groq(self, system_prompt: str, user_prompt: str) -> str:
        if not self.settings.groq_api_key:
            raise requests.RequestException("Missing GROQ_API_KEY")

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.settings.groq_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.settings.default_llm_model,
                "messages": self._messages(system_prompt, user_prompt),
                "temperature": 0.2,
                "max_tokens": 350,
            },
            timeout=30,
        )
        return self._parse_chat_response(response)

    def _call_openrouter(self, system_prompt: str, user_prompt: str) -> str:
        if not self.settings.openrouter_api_key:
            raise requests.RequestException("Missing OPENROUTER_API_KEY")

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.settings.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://127.0.0.1:8000",
                "X-Title": "AI Context Operating System",
            },
            json={
                "model": self.settings.default_llm_model,
                "messages": self._messages(system_prompt, user_prompt),
                "temperature": 0.2,
                "max_tokens": 350,
            },
            timeout=30,
        )
        return self._parse_chat_response(response)

    def _call_together(self, system_prompt: str, user_prompt: str) -> str:
        if not self.settings.together_api_key:
            raise requests.RequestException("Missing TOGETHER_API_KEY")

        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.settings.together_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.settings.default_llm_model,
                "messages": self._messages(system_prompt, user_prompt),
                "temperature": 0.2,
                "max_tokens": 350,
            },
            timeout=30,
        )
        return self._parse_chat_response(response)

    def _clean_output(self, text: str) -> str:
        text = re.sub(r"[*_`#>-]+", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()
