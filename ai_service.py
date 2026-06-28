import os
import google.generativeai as genai

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-2.5-flash")


# =========================
# TEXT AI
# =========================
def ask_gemini(prompt: str):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {str(e)}"


# =========================
# IMAGE AI (Gemini Vision)
# =========================
def detect_crop_disease(image):
    try:

        prompt = """
You are Agri AI Assist, an agricultural AI expert.

Analyze this crop image carefully.

Return ONLY valid JSON.

Use this exact format:

{
  "crop": "",
  "disease": "",
  "confidence": "",
  "symptoms": "",
  "causes": "",
  "recommendations": "",
  "prevention": ""
}

Rules:
- If the crop is healthy, set "disease" to "Healthy".
- Set confidence as High, Medium, or Low.
- Keep recommendations short and practical.
- Do NOT include markdown.
- Do NOT explain.
- Return JSON only.
"""

        response = model.generate_content([
            prompt,
            image
        ])

        return response.text

    except Exception as e:
        return f"AI Error: {str(e)}"
