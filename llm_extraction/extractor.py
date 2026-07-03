import json
import logging
import os

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = (
    "Extract the following fields from this receipt image and return ONLY valid JSON "
    "with no markdown formatting, no code fences, no explanation:\n"
    "{\n"
    '  "amount": <float in PKR>,\n'
    '  "date": "YYYY-MM-DD",\n'
    '  "time": "HH:MM (24hr)",\n'
    '  "merchant": "<merchant name>",\n'
    '  "category": "Food|Transport|Shopping|Utility|Health|Other",\n'
    '  "description": "<one-line description>"\n'
    "}\n"
    "If you cannot read the image clearly, make your best guess."
)


def _parse_response(response_text: str) -> dict | None:
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        cleaned = cleaned.rsplit("```", 1)[0]
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    try:
        start = cleaned.index("{")
        end = cleaned.rindex("}") + 1
        return json.loads(cleaned[start:end])
    except (ValueError, json.JSONDecodeError):
        return None


def extract_with_gemini(image_bytes: bytes, mime_type: str) -> dict | None:
    try:
        import google.generativeai as genai

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not set")
            return None
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            [
                {"mime_type": mime_type, "data": image_bytes},
                EXTRACTION_PROMPT,
            ]
        )
        if not response.text:
            return None
        return _parse_response(response.text)
    except Exception as e:
        logger.warning("Gemini extraction failed: %s", e)
        return None


def extract_with_groq(image_bytes: bytes, mime_type: str) -> dict | None:
    try:
        import base64

        from groq import Groq

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning("GROQ_API_KEY not set")
            return None
        client = Groq(api_key=api_key)
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{b64}"
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": data_url}},
                        {"type": "text", "text": EXTRACTION_PROMPT},
                    ],
                }
            ],
        )
        text = response.choices[0].message.content
        if not text:
            return None
        return _parse_response(text)
    except Exception as e:
        logger.warning("Groq extraction failed: %s", e)
        return None


def extract_receipt(image_bytes: bytes, mime_type: str) -> dict | None:
    result = extract_with_gemini(image_bytes, mime_type)
    if result:
        return result
    result = extract_with_groq(image_bytes, mime_type)
    if result:
        return result
    return None
