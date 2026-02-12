import json
import logging
import os

import google.generativeai as genai

logger = logging.getLogger(__name__)

try:
    from config import get_gemini_api_key

    API_KEY = get_gemini_api_key()
except Exception:
    API_KEY = None

INPUT_DIR = "AMANI_Training_Data"

if API_KEY:
    genai.configure(api_key=API_KEY)


def _redact(text):
    try:
        from privacy_guard import redact_text

        return redact_text(text)
    except Exception:
        return text, {"email": 0, "phone": 0, "ssn": 0, "cn_id": 0}


def run_diagnostic():
    print("=== A.M.A.N.I. Diagnostic Mode ===")
    print(
        f"Testing with Key: {API_KEY[:5]}...{API_KEY[-4:]}"
        if API_KEY
        else "No GEMINI_API_KEY set in .env"
    )

    if not os.path.exists(INPUT_DIR):
        print(f"CRITICAL: Directory '{INPUT_DIR}' does not exist.")
        return

    files = [f for f in os.listdir(INPUT_DIR) if f.endswith("_training_set.json")]
    if not files:
        print(f"CRITICAL: No data files found in {INPUT_DIR}")
        return

    print(f"Files found: {len(files)} JSON files.")
    first_file = os.path.join(INPUT_DIR, files[0])

    try:
        with open(first_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not data:
                print("CRITICAL: JSON file is empty.")
                return
            sample_case = data[0]
            print(f"Sample case loaded. PMID: {sample_case.get('pmid')}")
            print(f"Abstract length: {len(sample_case.get('abstract', ''))} chars")
    except Exception as e:
        print(f"CRITICAL: Error reading file: {e}")
        return

    print("\n>>> Test 1: Basic API Connectivity...")
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Say 'Hello A.M.A.N.I.' if you can hear me.")
        print(f"Connection Success! Response: {response.text.strip()}")
    except Exception as e:
        print("Connection FAILED.")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        return

    print("\n>>> Test 2: Medical Content Processing (Safety Filters)...")
    try:
        test_abstract = sample_case.get("abstract", "")[:300]
        safe_abstract, stats = _redact(test_abstract)
        if any(stats.values()):
            logger.info("Outbound payload redacted for debug_api: %s", stats)

        prompt = f"Extract medical entities from this text: {safe_abstract}"
        response = model.generate_content(prompt)

        if response.prompt_feedback and response.prompt_feedback.block_reason:
            print(f"BLOCKED. Reason: {response.prompt_feedback.block_reason}")
            print(f"Safety Ratings: {response.prompt_feedback.safety_ratings}")
        else:
            try:
                print(f"Medical Processing Success! Output preview: {response.text[:50]}...")
            except ValueError:
                print("Response blocked by safety filters (No text returned).")
                if response.prompt_feedback:
                    print(f"Safety Ratings: {response.prompt_feedback.safety_ratings}")
    except Exception as e:
        print(f"Medical Processing Error: {e}")


if __name__ == "__main__":
    run_diagnostic()
