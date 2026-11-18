"""Command routing and optional AI conversation."""
from __future__ import annotations

import datetime as dt
import re
import subprocess
import webbrowser
from urllib.parse import quote_plus

from .config import settings


class Assistant:
    def __init__(self) -> None:
        self.client = None
        if settings.openai_api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.openai_api_key)
            except Exception as exc:
                print(f"[AI] Could not initialize optional AI client: {exc}")
        self.history: list[dict[str, str]] = []

    def handle(self, command: str) -> tuple[str, bool]:
        text = command.lower().strip()
        if not text:
            return "I didn't catch that. Please say it again.", False

        if re.search(r"\b(stop listening|shut down jarvis|exit jarvis|quit jarvis|goodbye)\b", text):
            return "Understood. Going offline. Goodbye.", True

        if re.search(r"\b(what time is it|tell me the time|current time)\b", text) or text == "time":
            return f"It is {dt.datetime.now().strftime('%I:%M %p')}.", False
        if re.search(r"\b(what is the date|what's the date|what day is it|today's date)\b", text) or text == "date":
            return f"Today is {dt.datetime.now().strftime('%A, %B %d, %Y')}.", False

        apps = {
            "notepad": ["notepad.exe"],
            "calculator": ["calc.exe"],
            "file explorer": ["explorer.exe"],
            "explorer": ["explorer.exe"],
            "task manager": ["taskmgr.exe"],
        }
        for label, executable in apps.items():
            if f"open {label}" in text or text == label:
                try:
                    subprocess.Popen(executable, shell=False)
                    return f"Opening {label}.", False
                except OSError as exc:
                    return f"I couldn't open {label}: {exc}", False

        if "open chatgpt" in text:
            webbrowser.open("https://chatgpt.com")
            return "Opening ChatGPT in your browser.", False
        if "open browser" in text or "open google" in text:
            webbrowser.open("https://www.google.com")
            return "Opening your browser.", False
        if text.startswith("search for ") or text.startswith("google "):
            query = text.removeprefix("search for ").removeprefix("google ").strip()
            if query:
                webbrowser.open("https://www.google.com/search?q=" + quote_plus(query))
                return f"Searching the web for {query}.", False

        if self.client:
            try:
                self.history.append({"role": "user", "content": text})
                self.history = self.history[-12:]
                response = self.client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are JARVIS, a concise, calm, polished Windows desktop assistant. "
                                "Speak naturally and warmly. Remember the conversation context provided. "
                                "Never claim to have performed an action unless a tool actually did it. "
                                "Do not provide destructive shell commands or pretend you can control "
                                "the computer beyond the explicitly available actions."
                            ),
                        },
                        *self.history,
                    ],
                    temperature=0.6,
                    max_tokens=300,
                )
                answer = response.choices[0].message.content or "I don't have an answer right now."
                self.history.append({"role": "assistant", "content": answer})
                self.history = self.history[-12:]
                return answer, False
            except Exception as exc:
                print(f"[AI] {exc}")
                return "I couldn't reach the AI service. Local commands are still available.", False

        return (
            "I can open apps, tell the time and date, and search the web. "
            "Add an API key in your .env file to enable natural AI conversation.",
            False,
        )
