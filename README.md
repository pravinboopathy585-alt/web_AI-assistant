# Voice Assistant Web App 🎙️

Python Voice Assistant - Browser-based Web Version!

## Project Structure
```
voice_assistant_web/
├── app.py               ← Flask backend (Python logic)
├── requirements.txt     ← Python packages
└── static/
    └── index.html       ← Frontend (HTML + JS + CSS)
```

## Installation & Run

```bash
# 1. Install packages
pip install flask wikipedia requests

# 2. Run the server
python app.py

# 3. Browser-ல் open பண்ணுங்க
http://localhost:5000
```

## Features
- 🎤 Voice Input (Browser Web Speech API - Chrome வேணும்)
- 🔊 Voice Output (Browser TTS)
- ⏰ Time & Date
- 📝 Notes (save & show)
- 🔔 Reminders (save & show)
- 🌤️ Weather (wttr.in API)
- 📖 Wikipedia Search
- 🔍 Google Web Search
- 📺 YouTube
- 💬 Type செய்யவும் முடியும்

## Voice Commands (examples)
- "What is the time"
- "Take a note"
- "Show my notes"
- "Set a reminder to drink water at 5 PM"
- "Weather in Chennai"
- "Search wikipedia for Python programming"
- "Search for best restaurants near me"
- "Open YouTube"
- "Goodbye"

## Notes
- Voice input: Chrome browser மட்டும் support பண்ணும்
- Internet connection வேண்டும் (weather + wikipedia)
- Notes & reminders `assistant_data.json` file-ல் save ஆகும்
