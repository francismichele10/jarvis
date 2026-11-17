"""Speech input/output helpers."""
from __future__ import annotations
import json
import speech_recognition as sr
import pyttsx3
from .config import settings

class SpeechEngine:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.7
        self.microphone = sr.Microphone()
        self.tts = pyttsx3.init()
        self.tts.setProperty("rate", settings.voice_rate)
        self.tts.setProperty("volume", max(0.0, min(1.0, settings.voice_volume)))
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
