# translator.py
# Translates English text to Hindi
# Uses latest google-genai SDK with gemini-2.0-flash
# translator.py
# Translates English to Hindi using deep-translator
# Completely free — no API key, no account, no limits

from deep_translator import GoogleTranslator

translator = GoogleTranslator(source="en", target="hi")


def translate_to_hindi(english_text: str) -> str:
    if not english_text or not english_text.strip():
        return ""

    try:
        hindi = translator.translate(english_text)
        print(f"[Translator] EN: '{english_text}'")
        print(f"[Translator] HI: '{hindi}'")
        return hindi

    except Exception as e:
        print(f"[Translator] Error: {e}")
        return f"[Translation failed: {e}]"