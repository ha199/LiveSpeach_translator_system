# 🎙 SpeechTT — Real-Time Speech to Text + Hindi Translation

**Record → Whisper transcribes → Gemini translates → SQLite saves**

---

## ⚡ How it works

1. Click 🎤 → speak in English → click ⏹ stop
2. Full audio sent to **Whisper** (accurate, no gibberish)
3. English text sent to **Gemini 2.0 Flash** for Hindi translation
4. Both saved to **SQLite database** automatically
5. Results shown instantly on screen

---

## 🚀 Setup

### Step 1 — Install ffmpeg (required for Whisper on Windows)
```bash
winget install ffmpeg
```
Then close and reopen terminal.

### Step 2 — Install Python packages
```bash
cd backend
pip install -r requirements.txt
```

### Step 3 — Add Gemini API key
```bash
cp .env.example .env
```
Open `backend/.env` → paste your key from https://aistudio.google.com

### Step 4 — Run backend
```bash
python main.py
```

### Step 5 — Open frontend
Go to → **http://localhost:8000** in your browser

---

## 📁 Files

```
speechtt/
├── backend/
│   ├── main.py           FastAPI + WebSocket server
│   ├── transcriber.py    Whisper STT (full audio, accurate)
│   ├── translator.py     Gemini 2.0 Flash translation
│   ├── database.py       SQLite — saves english + hindi + timestamp
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    └── index.html        Complete UI — no npm needed
```

---

## 🗄 Database

SQLite file created automatically at `backend/transcriptions.db`

| Column | Type | Description |
|---|---|---|
| id | INTEGER | Auto increment |
| session_id | TEXT | WebSocket session |
| english_text | TEXT | Whisper output |
| hindi_text | TEXT | Gemini translation |
| status | TEXT | always "final" |
| timestamp | TEXT | UTC time |

---

## 🛠 Troubleshooting

| Error | Fix |
|---|---|
| Whisper error / no transcription | Install ffmpeg: `winget install ffmpeg` then restart terminal |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Red dot in UI | Run `python main.py` in backend folder |
| Gemini error | Check your API key in `backend/.env` |
