
import os
from openai import OpenAI


class Groq:
    def __init__(self, model: str):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )
        self.model = model

    def chat(self, messages, tools=None):
        params = {
            "model": self.model,
            "messages": messages,
            "max_completion_tokens": 4096,
            "extra_body": {"include_reasoning": False},
        }

        if tools:
            params["tools"] = tools

        return self.client.chat.completions.create(**params)

    def text_from_message(self, response):
        return response.choices[0].message.content or ""

    def add_assistant_message(self, messages, response):
        assistant_message = response.choices[0].message
        messages.append(
            assistant_message.model_dump(exclude_none=True)
        )

    def add_user_message(self, messages, content):
        messages.append({
            "role": "user",
            "content": content,
        })
