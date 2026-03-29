# transcriber.py
# Whisper STT — receives FULL audio file, transcribes all at once
# This gives accurate results (same approach as Colab notebook)
# Supports webm audio from browser MediaRecorder

import whisper
import tempfile
import os
import subprocess
import numpy as np

import imageio_ffmpeg
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
print(f"[Whisper] ffmpeg: {FFMPEG_EXE}")

print("[Whisper] Loading small model...")
model = whisper.load_model("small")
print("[Whisper] Model ready ✓")


def transcribe_audio_bytes(audio_bytes: bytes, ext: str = ".webm") -> str:
    if not audio_bytes or len(audio_bytes) < 1000:
        print("[Whisper] Audio too short")
        return ""

    tmp_webm = None

    try:
        # Write webm to temp file
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
            f.write(audio_bytes)
            tmp_webm = f.name

        print(f"[Whisper] Converting {len(audio_bytes)//1024}KB webm → numpy array...")

        # Use imageio ffmpeg to convert webm → raw PCM float32
        # Output to stdout as raw bytes — no temp wav file needed
        cmd = [
            FFMPEG_EXE,
            "-nostdin",
            "-threads", "0",
            "-i", tmp_webm,
            "-f", "s16le",      # raw 16-bit PCM
            "-ac", "1",         # mono
            "-acodec", "pcm_s16le",
            "-ar", "16000",     # 16kHz
            "-"                 # output to stdout
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30
        )

        if result.returncode != 0:
            print(f"[Whisper] ffmpeg error: {result.stderr.decode(errors='ignore')[-300:]}")
            return ""

        if not result.stdout:
            print("[Whisper] ffmpeg produced no output")
            return ""

        # Convert raw PCM bytes → numpy float32 array
        audio_np = np.frombuffer(result.stdout, dtype=np.int16).astype(np.float32)
        audio_np = audio_np / 32768.0  # normalize to -1.0 to 1.0

        print(f"[Whisper] Audio array: {len(audio_np)} samples ({len(audio_np)/16000:.1f}s)")

        if len(audio_np) < 1600:
            print("[Whisper] Too short after conversion")
            return ""

        # Pass numpy array directly — Whisper does NOT call ffmpeg this way
        output = model.transcribe(
            audio_np,
            language="en",
            fp16=False,
            verbose=False,
            condition_on_previous_text=False
        )

        text = output["text"].strip()
        print(f"[Whisper] ✓ '{text}'")
        return text

    except subprocess.TimeoutExpired:
        print("[Whisper] ffmpeg timed out")
        return ""
    except Exception as e:
        import traceback
        print(f"[Whisper] Exception: {e}")
        print(traceback.format_exc())
        return ""

    finally:
        if tmp_webm and os.path.exists(tmp_webm):
            try:
                os.unlink(tmp_webm)
            except Exception:
                pass