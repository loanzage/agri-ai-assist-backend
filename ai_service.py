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
You are Agri AI Assist.

Analyze this crop image.

Identify:

1. Crop name
2. Disease or pest (if visible)
3. Confidence (High/Medium/Low)
4. Symptoms
5. Possible causes
6. Recommended treatment
7. Prevention tips

If the image is healthy, clearly state that the crop appears healthy.

Keep the answer practical and farmer-friendly.
"""

        response = model.generate_content([
            prompt,
            image
        ])

        return response.text

    except Exception as e:
        return f"AI Error: {str(e)}"
