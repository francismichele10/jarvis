"""Command routing and optional AI conversation."""
from __future__ import annotations
import datetime as dt
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
        if any(x in text for x in ("stop listening", "shut down jarvis", "exit jarvis", "goodbye")):
            return "Understood. Going offline. Goodbye.", True
        if "time" in text:
            return f"It is {dt.datetime.now().strftime('%I:%M %p')}.", False
        if "date" in text or "day is it" in text:
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
                        {"role": "system", "content": "You are JARVIS, a concise, calm, helpful Windows desktop assistant. Never claim to have performed an action unless a tool actually did it. Do not provide destructive shell commands."},
                        *self.history,
                    ],
                    temperature=0.6,
                    max_tokens=250,
                )
                answer = response.choices[0].message.content or "I don't have an answer right now."
                self.history.append({"role": "assistant", "content": answer})
                return answer, False
            except Exception as exc:
                print(f"[AI] {exc}")
                return "I couldn't reach the AI service. Local commands are still available.", False

        return "I can open apps, tell the time and date, and search the web. Add an API key in .env for AI conversation.", False
