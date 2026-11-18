# Project JARVIS

A Windows-first, voice-controlled desktop assistant. The wake word is **Jarvis** (not "Hey Jarvis").

## Included in this starter
- Wake-word listening for "Jarvis".
- Spoken replies using installed Windows text-to-speech voices.
- Automatic preference for selected English voices where available, with manual voice selection through .env settings.
- A calmer default speech rate, adjustable to taste.
- A command to list installed voices: \`python main.py --list-voices\`.
- A short conversational session: after waking JARVIS, ask follow-up questions without repeating the wake word. Say "go to sleep" to end the session.
- You can say a command in one phrase, such as "Jarvis, open Notepad".
- Allowlisted local commands: open Notepad, Calculator, File Explorer, Task Manager, browser, and ChatGPT; tell the time/date; search the web.
- Optional AI conversation through your own OpenAI API key, with a short rolling conversation history.
- Optional offline speech recognition using a separately downloaded Vosk model.

This is a starter foundation, not a fully autonomous system. It does not place phone calls or execute arbitrary shell commands.

## Requirements
- Windows 10/11 and Python 3.10+ (64-bit recommended)
- Microphone and speakers/headphones
- Internet for Google speech recognition and optional AI

## Install
Open PowerShell in this folder and run:

    py -3 -m venv .venv
    .\\.venv\\Scripts\\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt

If PyAudio installation fails on Windows, try:

    python -m pip install pipwin
    pipwin install pyaudio

## Voice setup
JARVIS uses voices already installed in Windows. The default speech rate is set to 145 for a calmer delivery, and JARVIS tries a preferred English voice if one is available on your PC. The exact sound depends on the voices installed in Windows; this code cannot guarantee a deep voice on every computer.

To see the voices installed on your PC, run:

    python main.py --list-voices

To select one, open your .env file and set a distinctive part of its displayed name, for example:

    VOICE_NAME=David
    VOICE_RATE=140
    VOICE_VOLUME=1.0

If the requested name is not installed, JARVIS falls back to its automatic selection. You can experiment with VOICE_RATE values around 135–155. Lower values speak more slowly; they do not change the voice's actual pitch. Restart JARVIS after changing .env.

## Optional AI setup
Copy .env.example to .env and add your own OPENAI_API_KEY. Never commit .env or publish API keys. The .gitignore excludes it. AI conversation requires internet and API access, and API usage may incur charges.

## Run
    python main.py

Say "Jarvis", wait for "Yes? I'm listening", then speak. You can also say the wake word and command together:
- "Jarvis, open Notepad"
- "Jarvis, what time is it?"
- "Open Calculator" (as a follow-up during the active conversation)
- "Search for Python tutorials"
- "Go to sleep" to end the active conversation
- "Stop listening" to close JARVIS

You can also double-click run_jarvis.bat after installation. Press Ctrl+C to quit.

## Optional offline speech recognition
1. Download a small English model from https://alphacephei.com/vosk/models
2. Extract it under models/ (for example models/vosk-model-small-en-us-0.15).
3. Install Vosk: pip install vosk
4. Set VOSK_MODEL_PATH=models/vosk-model-small-en-us-0.15 in .env and restart.

When configured, Vosk is used for local transcription. Otherwise speech recognition uses Google's online service. Note that this version's wake-word detection is speech-recognition based, not a dedicated low-power hotword engine.

## Safety and privacy
The microphone is actively used while JARVIS is running. Google recognition sends audio to Google's service; Vosk can transcribe locally. Optional AI sends recognized text to the configured OpenAI API. Local app commands are explicitly allowlisted. Startup-on-boot, phone calls, and consequential system controls are not enabled in this starter.

## Roadmap
1. Dedicated low-latency wake-word engine.
2. Polished Windows interface and optional startup integration.
3. More Windows controls with confirmation for consequential actions.
4. Improved offline speech and local AI.
5. Permission-based phone/contact integration where supported.
