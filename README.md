# 🎙 SpeechTT — Real-Time Speech to Text + Hindi Translation

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Whisper](https://img.shields.io/badge/Whisper-Small-412991?style=for-the-badge&logo=openai&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-2.0_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![WebSocket](https://img.shields.io/badge/WebSocket-Real--Time-FF6B35?style=for-the-badge)

**Record English speech → Whisper transcribes →  deep-translator, translates to Hindi → Saved to database**

</div>

---

## 📌 What is SpeechTT?

SpeechTT is a real-time Speech-to-Text service that:

1. Records live English speech from your microphone in the browser
2. Sends the complete audio to **OpenAI Whisper** (runs locally, completely free)
3. Translates the English text to **Hindi** using ** deep-translator running locally 
4. Saves both `english_text` and `hindi_text` with timestamp to a **SQLite database**
5. Shows results instantly on screen with a live pipeline status indicator

---

## 🏗 Architecture
```
Browser (Microphone)
        │
        │  User clicks 🎤, speaks, clicks ⏹ stop
        │  Full audio sent as one WebSocket binary message
        ▼
FastAPI Backend — ws://localhost:8000/ws/transcribe
        │
        ├── 1. imageio_ffmpeg
        │      Converts webm audio → raw PCM numpy array
        │
        ├── 2. Whisper Small Model (local, free)
        │      numpy array → English text
        │      No ffmpeg PATH needed — runs completely in memory
        │
        ├── 3.  deep-translator (free  No API) first i tried gimini model but it has limit issue
        │      English text → Hindi translation
        │
        ├── 4. SQLite Database
        │      Saves english_text, hindi_text, session_id, timestamp, status
        │
        └── 5. WebSocket Response
               Sends result back to browser instantly
```

---

## ✨ Features

- 🎤 **Live microphone recording** — click to start, click to stop
- 🎯 **Accurate transcription** — records full audio before processing, no streaming chunks
- 🇮🇳 **Hindi translation** — instant using  deep-translator Locally
- 💾 **SQLite database** — zero setup, saves automatically as a local file
- 📋 **History panel** — all past transcriptions visible on screen
- 🟢 **Live status indicator** — shows connection, recording, processing states
- 🔄 **Pipeline steps** — visual indicator shows Record → Whisper → Gemini → DB → Done
- 🗑 **Clear history** — delete all records with one click
- 📡 **REST API** — query transcriptions via HTTP endpoints

---

## 🏗 Tech Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| WebSocket | FastAPI WebSocket |
| Speech-to-Text | OpenAI Whisper (small model, runs locally) |
| Audio Conversion | imageio-ffmpeg (bundled, no system install) |
| Translation |  deep-translator |
| Database | SQLite (zero setup, single file) |
| Frontend | Plain HTML + CSS + Vanilla JavaScript |

---

## 📁 Project Structure
```
speechtt/
│
├── backend/
│   ├── main.py              ← FastAPI server + WebSocket endpoint
│   ├── transcriber.py       ← Whisper STT using imageio ffmpeg
│   ├── translator.py        ← G deep-translator Hindi translation
│   ├── database.py          ← SQLite save, fetch, clear operations
│   ├── requirements.txt     ← All Python dependencies
│   └── .env.example         ← Copy to .env and add your Gemini key
│
└── frontend/
    └── index.html           ← Complete UI — no npm or Node.js needed
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** → https://python.org/downloads
- 

---

### Step 1 — Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/speechtt.git
cd speechtt
```

---

---

### Step 3 — Create Virtual Environment (recommended)
```bash
cd backend
python -m venv .venv
```

Activate it:

**Windows:**
```bash
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

You will see `(.venv)` at the start of your terminal line — this means it is active.

---

### Step 4 — Install Dependencies

Make sure you are inside the `backend` folder with `.venv` active, then:
```bash
pip install -r requirements.txt
```

> ⚠️ First time takes 5–10 minutes — downloads Whisper small model (~460MB) and PyTorch.


### Step 6 — Run the Backend
```bash
python main.py
```

You will see:
```
[Whisper] ffmpeg: ...imageio_ffmpeg\binaries\ffmpeg-win-x86_64...
[Whisper] Loading small model...
[Whisper] Model ready ✓
[DB] SQLite ready → ...backend\transcriptions.db
🎙  SpeechTT Backend
    Frontend  →  http://localhost:8000
    API Docs  →  http://localhost:8000/docs
```

---

### Step 7 — Open the Frontend

Open your browser and go to → **http://localhost:8000**

The UI will show a **🟢 green dot** when the backend is connected and ready.

---

## 🖥 How to Use

1. Open **http://localhost:8000** in your browser
2. Wait for the **🟢 green dot** — backend connected
3. Click the **🎤 microphone button**
4. Allow microphone access when browser asks
5. Speak clearly in English
6. Click **⏹ stop** when done speaking
7. Watch the pipeline steps light up — Record → Whisper → Gemini → DB → Done
8. English transcription and Hindi translation appear on screen
9. Result is automatically saved to the database
10. All past transcriptions shown in the history panel below

---

Here you will see the UI like this whcih having all features 

<img width="1600" height="1116" alt="image" src="https://github.com/user-attachments/assets/abb09d45-e9c5-474b-b005-d9ac325dec24" />


## 📡 API Reference

### Health Check
```http
GET http://localhost:8000/health
```
```json
{
  "status": "ok",
  "stt_model": "whisper-small",
  "translation_model": " deep-translator",
  "database": "sqlite"
}
```

### Get All Transcriptions
```http
GET http://localhost:8000/api/transcriptions?limit=50
```

### Clear All Transcriptions
```http
DELETE http://localhost:8000/api/transcriptions
```

### WebSocket Endpoint
```
ws://localhost:8000/ws/transcribe
```

**Flow:**
1. Connect → server sends `session_start` with `session_id`
2. Send full audio as binary message
3. Server sends `processing` updates
4. Server sends `result` with english and hindi text
5. Repeat for next recording

---

## 🗄 Database Schema

SQLite file created automatically at `backend/transcriptions.db`
```sql
CREATE TABLE transcriptions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id    TEXT    NOT NULL,
    english_text  TEXT    NOT NULL,
    hindi_text    TEXT    NOT NULL,
    status        TEXT    NOT NULL DEFAULT 'final',
    timestamp     TEXT    NOT NULL
);
```

---

## 🛠 Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Activate venv first: `.venv\Scripts\activate` then `pip install -r requirements.txt` |
| Red dot — backend not connecting | Make sure `python main.py` is running in backend folder |
| Microphone not working | Click allow when browser asks for microphone permission |
| No transcription / blank result | Speak clearly for at least 2–3 seconds before stopping |
| Whisper WinError 2 | Already fixed — uses `imageio_ffmpeg` bundled binary |
| Slow first transcription | Normal — Whisper loads model on first use |


---

## 📋 Assignment Coverage

| Requirement | Implementation |
|---|---|
| Accept live audio input | Browser MediaRecorder API via WebSocket |
| Real-time audio streaming | WebSocket binary stream |
| Speech to English text | OpenAI Whisper small model |
| Translate to Hindi | first i used Google Gemini 2.0 Flash but it havnig qouta limit issue then i changed to  |  deep-translator running localy no api
| Store english_text | SQLite `transcriptions` table |
| Store hindi_text | SQLite `transcriptions` table |
| Store timestamp | UTC ISO format in SQLite |
| Store final/partial status | `status` column — always `final` (full audio approach) |
| Streaming response | WebSocket pushes processing updates and final result |
| REST API | GET and DELETE endpoints for transcriptions |

---

## 📄 License

Hari Hold All rights — free to use and modify.

---

<div align="center">
Built with OpenAI Whisper ·  deep-translator · FastAPI · SQLite
</div>
