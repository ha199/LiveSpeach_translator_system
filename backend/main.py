# main.py
# FastAPI backend — receives full audio via WebSocket, transcribes, translates, saves to DB

import os
import json
import uuid
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


from database import init_db, save_transcription, get_all_transcriptions, delete_all
from transcriber import transcribe_audio_bytes
from translator import translate_to_hindi


# ── Init DB ─────────────────────────────────────────────────────
init_db()

# ── App ─────────────────────────────────────────────────────────
app = FastAPI(title="SpeechTT", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
FRONTEND_PATH = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(FRONTEND_PATH):
    app.mount("/static", StaticFiles(directory=FRONTEND_PATH), name="static")


# ── REST endpoints ───────────────────────────────────────────────

@app.get("/")
def root():
    index = os.path.join(FRONTEND_PATH, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"status": "SpeechTT running", "docs": "/docs"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "stt_model": "whisper-small",
        "translation_model": "gemini-2.0-flash",
        "database": "sqlite"
    }


@app.get("/api/transcriptions")
def list_transcriptions(limit: int = 50):
    records = get_all_transcriptions(limit)
    return {"count": len(records), "data": records}


@app.delete("/api/transcriptions")
def clear_transcriptions():
    count = delete_all()
    return {"message": f"Deleted {count} records"}


# ── WebSocket ────────────────────────────────────────────────────
# Protocol:
#   1. Client connects
#   2. Server sends session_start with session_id
#   3. Client records audio completely
#   4. Client sends full audio as ONE binary message
#   5. Server transcribes → translates → saves → sends result back
#   6. Client can record again for next utterance

@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())

    print(f"\n[WS] New session: {session_id}")

    # Greet client
    await websocket.send_text(json.dumps({
        "type":       "session_start",
        "session_id": session_id,
        "message":    "Ready. Record audio and send when done."
    }))

    try:
        while True:
            data = await websocket.receive()

            # ── Full audio blob received ──────────────────────
            if "bytes" in data and data["bytes"]:
                audio_bytes = data["bytes"]
                print(f"[WS] Received {len(audio_bytes) // 1024}KB audio")

                # Tell client we are working
                await websocket.send_text(json.dumps({
                    "type":    "processing",
                    "message": "Transcribing with Whisper..."
                }))

                # Step 1: Speech to Text (Whisper)
                english_text = transcribe_audio_bytes(audio_bytes, ext=".webm")

                if not english_text:
                    await websocket.send_text(json.dumps({
                        "type":    "error",
                        "message": "Could not transcribe audio. Speak clearly and try again."
                    }))
                    continue

                # Tell client translation is happening
                await websocket.send_text(json.dumps({
                    "type":    "processing",
                    "message": "Translating to Hindi..."
                }))

                # Step 2: Translate to Hindi (Gemini)
                hindi_text = translate_to_hindi(english_text)

                # Step 3: Save to SQLite database
                row_id = save_transcription(
                    session_id=session_id,
                    english_text=english_text,
                    hindi_text=hindi_text,
                    status="final"
                )

                # Step 4: Send result back to client
                await websocket.send_text(json.dumps({
                    "type":         "result",
                    "id":           row_id,
                    "session_id":   session_id,
                    "english_text": english_text,
                    "hindi_text":   hindi_text,
                    "status":       "final",
                    "timestamp":    datetime.utcnow().isoformat()
                }))

            # ── Text control message ──────────────────────────
            elif "text" in data:
                msg = data["text"].strip()
                if msg == "PING":
                    await websocket.send_text(json.dumps({"type": "pong"}))

    except WebSocketDisconnect:
        print(f"[WS] Session ended: {session_id}")
    except Exception as e:
        print(f"[WS] Error: {e}")
        try:
            await websocket.send_text(json.dumps({
                "type":    "error",
                "message": str(e)
            }))
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn
    print("\n🎙  SpeechTT Backend")
    print("    Frontend  →  http://localhost:8000")
    print("    API Docs  →  http://localhost:8000/docs\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
