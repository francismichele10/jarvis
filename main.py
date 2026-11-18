"""Project JARVIS entry point. Run with: python main.py"""
import re
import sys

from jarvis.assistant import Assistant
from jarvis.config import settings
from jarvis.speech import SpeechEngine, available_voices


def contains_wake_word(phrase: str) -> bool:
    """Match Jarvis as a separate word, not as part of another word."""
    return re.search(rf"\b{re.escape(settings.wake_word)}\b", phrase, re.IGNORECASE) is not None


def remove_wake_word(phrase: str) -> str:
    """Return anything spoken after the wake word, if present."""
    return re.sub(
        rf"\b{re.escape(settings.wake_word)}\b[,:;.!]?\s*",
        "",
        phrase,
        count=1,
        flags=re.IGNORECASE,
    ).strip()


def main() -> None:
    if "--list-voices" in sys.argv:
        try:
            voices = available_voices()
            if not voices:
                print("No installed speech voices were detected.")
            else:
                print("Installed Windows speech voices:")
                for name, voice_id in voices:
                    print(f"- {name} | ID: {voice_id}")
                print("\nSet VOICE_NAME in your .env file to select one.")
        except Exception as exc:
            print(f"Could not list speech voices: {exc}")
            sys.exit(1)
        return

    print("=" * 54)
    print(" PROJECT JARVIS | Windows voice assistant")
    print(f' Wake word: "{settings.wake_word.title()}"')
    print(" Say 'Jarvis' to start. Say 'go to sleep' to end a chat.")
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
            if not contains_wake_word(heard):
                continue

            command = remove_wake_word(heard)
            if not command:
                speech.speak("Yes? I'm listening.")
                command = speech.listen(timeout=7, phrase_time_limit=10)

            while command:
                print(f"[Command] {command}")
                normalized = command.lower().strip()
                if normalized in {"go to sleep", "that's all", "that is all", "thanks jarvis", "thank you jarvis"}:
                    speech.speak("Of course. I'll be here when you need me.")
                    break

                reply, should_exit = assistant.handle(command)
                speech.speak(reply)
                if should_exit:
                    return

                command = speech.listen(timeout=8, phrase_time_limit=12)
                if not command:
                    speech.speak("I'll go quiet for now. Say Jarvis when you need me.")
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
