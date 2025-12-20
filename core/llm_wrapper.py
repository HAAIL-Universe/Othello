import os
import openai
import logging
from typing import Optional
from dotenv import load_dotenv
from utils.llm_config import get_openai_api_key

def pick_model(default: str = "gpt-4o"):
    print("Which model would you like FELLO to use this session?")
    print("1: gpt-3.5-turbo")
    print("2: gpt-4")
    print("3: gpt-4-turbo")
    print("4: gpt-4o")
    choice = input(f"Enter 1-4 [default={default}]: ").strip()
    # The following lines were incorrectly indented and are now fixed
    model_cache_path = ".llm_model_cache"
    resolved_model = None
    model = None
    if choice in {"1", "2", "3", "4"}:
        model = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"][int(choice)-1]
    if model:
        resolved_model = model
    else:
        env_model = os.getenv("OTHELLO_MODEL")
        if env_model:
            resolved_model = env_model
        elif os.path.exists(model_cache_path):
            with open(model_cache_path, "r") as f:
                resolved_model = f.read().strip()
        else:
            resolved_model = "gpt-4o"

    # Only write cache if model was explicitly set (argument or env)
    if model or (not model and os.getenv("OTHELLO_MODEL")):
        with open(model_cache_path, "w") as f:
            f.write(resolved_model)
    return resolved_model


class LLMWrapper:
    def __init__(self, model: Optional[str] = None):
        load_dotenv(override=False)
        api_key = get_openai_api_key()
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set or empty.")

        self.client = openai.OpenAI(api_key=api_key)

        # Check for cached model
        model_cache_path = ".llm_model_cache"
        if model:
            self.model = model
            with open(model_cache_path, "w") as f:
                f.write(model)
        elif os.path.exists(model_cache_path):
            with open(model_cache_path, "r") as f:
                self.model = f.read().strip()
        else:
            self.model = pick_model()
            with open(model_cache_path, "w") as f:
                f.write(self.model)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 300) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            logging.debug("Making API call to OpenAI...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=10  # Set timeout for 10 seconds
            )
            logging.debug("API call completed.")
            response_content = response.choices[0].message.content
            if response_content is not None:
                return response_content.strip()
            return "[LLM Error]: No content returned from LLM."
        except Exception as e:
            status = getattr(e, "status_code", None)
            request_id = None
            error_body = None
            try:
                resp = getattr(e, "response", None)
                if resp is not None:
                    request_id = getattr(resp, "headers", {}).get("x-request-id")
                    if hasattr(resp, "json"):
                        error_body = resp.json()
                    elif hasattr(resp, "text"):
                        error_body = resp.text
            except Exception:
                pass
            logging.error(
                "OpenAI chat.completions error: %s status=%s request_id=%s body=%s",
                type(e).__name__,
                status,
                request_id,
                error_body,
                exc_info=True,
            )
            raise ValueError("OpenAI chat completion failed") from e

class AsyncLLMWrapper(LLMWrapper):
    async def chat(self, messages):
        # messages is a list of dicts: [{role: ..., content: ...}]
        # Pull out system and user prompt for .generate()
        system_prompt = None
        user_prompt = ""
        for msg in messages:
            if msg.get("role") == "system":
                system_prompt = msg.get("content")
            elif msg.get("role") == "user":
                user_prompt = msg.get("content")
        # Run synchronous generate() in a thread so async works
        import asyncio
        return await asyncio.to_thread(self.generate, user_prompt, system_prompt)
