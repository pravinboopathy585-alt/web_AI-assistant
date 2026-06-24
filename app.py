

from flask import Flask, request, jsonify, send_from_directory
import datetime
import json
import os
import webbrowser
import wikipedia
import requests as req

app = Flask(__name__, static_folder="static", template_folder="static")

DATA_FILE = os.path.join(os.path.dirname(__file__), "assistant_data.json")
DEFAULT_DATA = {"notes": [], "reminders": []}


# ---------- Data Persistence ---------- #
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump(DEFAULT_DATA, f, indent=4)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------- Serve Frontend ---------- #
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# ---------- Command Handler ---------- #
@app.route("/command", methods=["POST"])
def handle_command():
    body = request.get_json()
    command = (body.get("command") or "").lower().strip()
    extra = (body.get("extra") or "").lower().strip()

    if not command:
        return jsonify({"reply": "I didn't catch that. Please try again."})

    data = load_data()
    reply = ""
    action = None
    action_data = None

    # Time
    if "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        reply = f"The current time is {now}."

    # Date
    elif "date" in command or "today" in command:
        today = datetime.datetime.now().strftime("%A, %d %B %Y")
        reply = f"Today is {today}."

    # Add Note
    elif "note" in command and any(w in command for w in ["take", "add", "write", "save"]):
        if extra:
            note = {"text": extra, "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
            data["notes"].append(note)
            save_data(data)
            reply = f"Got it! I've saved your note: \"{extra}\""
        else:
            reply = "What should I note down?"
            action = "ask_note"

    # Show Notes
    elif "show" in command and "note" in command:
        notes = data["notes"]
        if notes:
            reply = f"You have {len(notes)} note(s)."
            action = "show_notes"
            action_data = [{"text": n["text"], "created": n.get("created", "")} for n in notes]
        else:
            reply = "You have no notes saved yet."

    # Clear Notes
    elif "clear" in command and "note" in command:
        data["notes"] = []
        save_data(data)
        reply = "All notes have been cleared."

    # Add Reminder
    elif "remind" in command and ("set" in command or "add" in command or "remind" == command.split()[0]):
        if extra:
            parts = extra.split(" at ", 1)
            text = parts[0].strip()
            when = parts[1].strip() if len(parts) > 1 else "unspecified"
            reminder = {"text": text, "when": when}
            data["reminders"].append(reminder)
            save_data(data)
            reply = f"Reminder set: \"{text}\" at {when}."
        else:
            reply = "What should I remind you about? (You can say: remind me to drink water at 5 PM)"
            action = "ask_reminder"

    # Show Reminders
    elif "show" in command and "remind" in command:
        reminders = data["reminders"]
        if reminders:
            reply = f"You have {len(reminders)} reminder(s)."
            action = "show_reminders"
            action_data = reminders
        else:
            reply = "You have no reminders saved yet."

    # Clear Reminders
    elif "clear" in command and "remind" in command:
        data["reminders"] = []
        save_data(data)
        reply = "All reminders have been cleared."

    # Wikipedia
    elif "wikipedia" in command:
        query = command.replace("search", "").replace("wikipedia", "").replace("for", "").strip()
        if query:
            try:
                summary = wikipedia.summary(query, sentences=2)
                reply = summary
            except wikipedia.exceptions.DisambiguationError:
                reply = "Multiple results found. Please be more specific."
            except wikipedia.exceptions.PageError:
                reply = f"No Wikipedia article found for '{query}'."
            except Exception:
                reply = "Wikipedia search failed. Please try again."
        else:
            reply = "What should I search on Wikipedia?"

    # Weather
    elif "weather" in command:
        city = command.replace("weather", "").replace("in", "").replace("what", "").replace("is", "").replace("the", "").strip()
        if not city and extra:
            city = extra
        if city:
            try:
                url = f"https://wttr.in/{city}?format=%C+%t"
                resp = req.get(url, timeout=5)
                if resp.status_code == 200:
                    reply = f"Weather in {city.title()}: {resp.text.strip()}"
                else:
                    reply = "Could not fetch weather right now."
            except Exception:
                reply = "Weather service unavailable. Please try again."
        else:
            reply = "Which city's weather would you like to know?"
            action = "ask_weather"

    # YouTube
    elif "youtube" in command:
        query = command.replace("youtube", "").replace("open", "").replace("play", "").replace("search", "").strip()
        url = f"https://www.youtube.com/results?search_query={query}" if query else "https://www.youtube.com"
        reply = f"Opening YouTube{' for: ' + query if query else ''}."
        action = "open_url"
        action_data = url

    # Web Search
    elif "search" in command:
        query = command.replace("search", "").replace("for", "").strip()
        if query:
            reply = f"Searching the web for: {query}"
            action = "open_url"
            action_data = f"https://www.google.com/search?q={query}"
        else:
            reply = "What would you like me to search for?"

    # Greeting
    elif any(w in command for w in ["hello", "hi", "hey", "good morning", "good evening", "good afternoon"]):
        hour = datetime.datetime.now().hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        reply = f"{greeting}! I'm your voice assistant. How can I help you today?"

    # Help
    elif "help" in command or "what can you do" in command:
        reply = ("I can help you with: checking time and date, taking notes, "
                 "setting reminders, searching Wikipedia, checking weather, "
                 "opening YouTube, searching the web. Just ask me anything!")

    # Exit
    elif any(w in command for w in ["bye", "exit", "stop", "quit", "goodbye"]):
        reply = "Goodbye! Have a wonderful day. Come back anytime!"
        action = "exit"

    else:
        reply = ("I didn't understand that. Try asking about: time, date, "
                 "notes, reminders, weather, Wikipedia, or web search.")

    response = {"reply": reply}
    if action:
        response["action"] = action
    if action_data is not None:
        response["action_data"] = action_data

    return jsonify(response)


if __name__ == "__main__":
    print("🎙️  Voice Assistant Web App starting...")
    print("👉  Open your browser at: http://localhost:5000")
    app.run(debug=True, port=5000)
