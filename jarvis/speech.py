"""Speech input/output helpers."""
from __future__ import annotations

import json
import speech_recognition as sr
import pyttsx3

from .config import settings


def _voice_languages(voice) -> str:
    values = []
    for language in getattr(voice, "languages", []) or []:
        if isinstance(language, bytes):
            language = language.decode("utf-8", errors="ignore")
        values.append(str(language))
    return " ".join(values).lower()


def choose_voice(voices):
    """Choose a requested voice, otherwise prefer a natural English voice."""
    if not voices:
        return None

    requested_id = settings.voice_id.strip().lower()
    requested_name = settings.voice_name.strip().lower()

    if requested_id:
        for voice in voices:
            if str(getattr(voice, "id", "")).lower() == requested_id:
                return voice

    if requested_name:
        for voice in voices:
            if requested_name in str(getattr(voice, "name", "")).lower():
                return voice

    # Windows commonly includes voices such as David or Mark. Prefer these
    # when available, but keep a reliable fallback for other Windows installs.
    preferred_names = ("david", "mark", "guy", "ryan", "christopher", "george", "james")
    english = [
        voice for voice in voices
        if "en" in _voice_languages(voice)
        or any(token in str(getattr(voice, "name", "")).lower() for token in preferred_names)
    ]
    candidates = english or list(voices)
    for preferred in preferred_names:
        for voice in candidates:
            if preferred in str(getattr(voice, "name", "")).lower():
                return voice
    return candidates[0]


def available_voices() -> list[tuple[str, str]]:
    """Return installed Windows speech voices as (name, id) pairs."""
    engine = pyttsx3.init()
    try:
        return [
            (str(getattr(voice, "name", "Unknown")), str(getattr(voice, "id", "")))
            for voice in engine.getProperty("voices")
        ]
    finally:
        engine.stop()


class SpeechEngine:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.7
        self.microphone = sr.Microphone()
        self.tts = pyttsx3.init()
        self.tts.setProperty("rate", settings.voice_rate)
        self.tts.setProperty("volume", max(0.0, min(1.0, settings.voice_volume)))

        voices = self.tts.getProperty("voices")
        selected_voice = choose_voice(voices)
        if selected_voice is not None:
            self.tts.setProperty("voice", selected_voice.id)
            print(f"[JARVIS] Voice selected: {selected_voice.name}")
        else:
            print("[JARVIS] No installed speech voices were detected; using system default.")

        self.vosk_model = None
        if settings.vosk_model_path:
            try:
                from vosk import Model
                self.vosk_model = Model(settings.vosk_model_path)
            except Exception as exc:
                print(f"[JARVIS] Offline Vosk model unavailable: {exc}")

    def speak(self, text: str) -> None:
        print(f"JARVIS: {text}")
        self.tts.say(text)
        self.tts.runAndWait()

    def listen(self, timeout: float | None = None, phrase_time_limit: float = 6.0) -> str:
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            return ""
        except Exception as exc:
            print(f"[Microphone] {exc}")
            return ""

        if self.vosk_model is not None:
            try:
                from vosk import KaldiRecognizer
                recognizer = KaldiRecognizer(self.vosk_model, 16000)
                raw = audio.get_raw_data(convert_rate=16000, convert_width=2)
                recognizer.AcceptWaveform(raw)
                result = json.loads(recognizer.FinalResult())
                transcript = result.get("text", "").strip()
                if transcript:
                    return transcript.lower()
            except Exception as exc:
                print(f"[Offline recognition] {exc}")

        try:
            return self.recognizer.recognize_google(audio).lower().strip()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as exc:
            print(f"[Speech service] {exc}")
            return ""
