import json
import logging
import os
import traceback

import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold, HarmCategory

logger = logging.getLogger(__name__)

try:
    from config import get_gemini_api_key

    API_KEY = get_gemini_api_key()
except Exception:
    API_KEY = None

INPUT_DIR = "AMANI_Training_Data"

if API_KEY:
    genai.configure(api_key=API_KEY)

MODEL_NAME = "models/gemini-2.5-flash"

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}


def _redact(text):
    try:
        from privacy_guard import redact_text

        return redact_text(text)
    except Exception:
        return text, {"email": 0, "phone": 0, "ssn": 0, "cn_id": 0}


def forensic_analysis():
    print(f"=== A.M.A.N.I. Forensic Analysis (Target: {MODEL_NAME}) ===")

    if not os.path.exists(INPUT_DIR):
        print("Data directory missing.")
        return

    files = [f for f in os.listdir(INPUT_DIR) if f.endswith("_training_set.json")]
    if not files:
        print("No data files found.")
        return

    first_file = os.path.join(INPUT_DIR, files[0])
    with open(first_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        case = data[0]

    print(f"Analyzed Case ID: {case.get('pmid', 'Unknown')}")
    print(f"Abstract Length: {len(case.get('abstract', ''))} chars")

    print("\n>>> Attempting Generation with verbose error logging...")

    try:
        model = genai.GenerativeModel(MODEL_NAME)

        raw_abstract = case.get("abstract", "")[:500]
        safe_abstract, stats = _redact(raw_abstract)
        if any(stats.values()):
            logger.info("Outbound payload redacted for forensic_debug: %s", stats)

        prompt = f"Extract medical entities from this text: {safe_abstract}"

        print("Sending request to Google...")
        response = model.generate_content(prompt, safety_settings=SAFETY_SETTINGS)

        print("\nSUCCESS! The API is working. Here is the raw response:")
        print("-" * 20)
        print(response.text)
        print("-" * 20)

    except Exception:
        print("\nFATAL ERROR DETECTED!")
        print("This is the exact reason why your 1200 cases failed:")
        print("=" * 40)
        traceback.print_exc()
        print("=" * 40)

        print("\n>>> Trying fallback model: models/gemini-2.0-flash-lite-preview-02-05 ...")
        try:
            fallback_model = genai.GenerativeModel("models/gemini-2.0-flash-lite-preview-02-05")
            res = fallback_model.generate_content("Hello")
            print(f"Fallback Model Works! Response: {res.text}")
        except Exception:
            print("Fallback Model also failed.")


if __name__ == "__main__":
    forensic_analysis()
