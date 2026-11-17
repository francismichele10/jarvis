"""Project JARVIS entry point. Run with: python main.py"""
import sys
import speech_recognition as sr
from jarvis.assistant import Assistant
from jarvis.config import settings
from jarvis.speech import SpeechEngine

def main() -> None:
    print("=" * 54)
    print(" PROJECT JARVIS | Windows voice assistant")
    print(f' Wake word: "{settings.wake_word.title()}"')
    print(" Press Ctrl+C to quit.")
    print("=" * 54)
    try:
        speech = SpeechEngine()
        assistant = Assistant()
        with speech.microphone as source:
            print("[JARVIS] Calibrating microphone noise level...")
            speech.recognizer.adjust_for_ambient_noise(source, duration=1)
        speech.speak("JARVIS is online. Say Jarvis when you need me.")
        while True:
            heard = speech.listen(timeout=None, phrase_time_limit=4)
            if not heard:
                continue
            print(f"[Heard] {heard}")
            if settings.wake_word not in heard:
                continue
            speech.speak("Yes? I'm listening.")
            command = speech.listen(timeout=7, phrase_time_limit=10)
            if not command:
                speech.speak("I didn't hear a command.")
                continue
            print(f"[Command] {command}")
            reply, should_exit = assistant.handle(command)
            speech.speak(reply)
            if should_exit:
                break
    except KeyboardInterrupt:
        print("\n[JARVIS] Stopped by keyboard.")
    except OSError as exc:
        print(f"[Setup error] {exc}")
        print("Check microphone connection and Windows desktop microphone permissions.")
        sys.exit(1)
    except Exception as exc:
        print(f"[JARVIS error] {exc}")
        sys.exit(1)

if __name__ == "__main__":
    main()
