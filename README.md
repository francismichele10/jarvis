# Project JARVIS

A Windows-first, voice-controlled desktop assistant. The wake word is **Jarvis** (not "Hey Jarvis").

## Included in this starter
- Continuous wake-word listening for "Jarvis".
- Spoken replies using Windows text-to-speech.
- Allowlisted local commands: open Notepad, Calculator, File Explorer, Task Manager, browser, and ChatGPT; tell the time/date; search the web.
- Optional AI conversation through your own OpenAI API key.
- Optional offline speech recognition using a separately downloaded Vosk model.

This is a starter foundation, not a fully autonomous system. It does not place phone calls or execute arbitrary shell commands.

## Requirements
- Windows 10/11 and Python 3.10+ (64-bit recommended)
- Microphone and speakers/headphones
- Internet for Google speech recognition and optional AI

## Install
Open PowerShell in this folder and run:

    py -3 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt

If PyAudio installation fails on Windows, try:

    python -m pip install pipwin
    pipwin install pyaudio

## Optional AI setup
Copy .env.example to .env and add your own OPENAI_API_KEY. Never commit .env or publish API keys. The .gitignore excludes it. AI conversation requires internet and API access.

## Run
    python main.py

Say "Jarvis", wait for "Yes? I'm listening", then say a command:
- "Open Notepad"
- "Open Calculator"
- "Open File Explorer"
- "Open ChatGPT"
- "What time is it?"
- "Search for Python tutorials"
- "Stop listening"

You can also double-click run_jarvis.bat after installation. Press Ctrl+C to quit.

## Optional offline speech recognition
1. Download a small English model from https://alphacephei.com/vosk/models
2. Extract it under models/ (for example models/vosk-model-small-en-us-0.15).
3. Install Vosk: pip install vosk
4. Set VOSK_MODEL_PATH=models/vosk-model-small-en-us-0.15 in .env and restart.

When configured, Vosk is used for local transcription. Otherwise speech recognition uses Google's online service. Note that this first version's wake-word detection is speech-recognition based, not a dedicated low-power hotword engine.

## Safety and privacy
The microphone is actively used while JARVIS is running. Google recognition sends audio to Google's service; Vosk can transcribe locally. Optional AI sends recognized text to the configured OpenAI API. Local app commands are explicitly allowlisted. Startup-on-boot, phone calls, and consequential system controls are not enabled in this starter.

## Roadmap
1. Dedicated low-latency wake-word engine.
2. Polished Windows interface and optional startup integration.
3. More Windows controls with confirmation for consequential actions.
4. Improved offline speech and local AI.
5. Permission-based phone/contact integration where supported.