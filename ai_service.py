import os
import json
import google.generativeai as genai


# =====================================================
# GEMINI CONFIGURATION
# =====================================================

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)


model = genai.GenerativeModel(
    "gemini-2.5-flash"
)



# =====================================================
# GENERAL AI CHAT
# =====================================================

def ask_gemini(prompt: str):

    try:

        response = model.generate_content(
            prompt
        )

        return response.text


    except Exception as e:

        return f"AI Error: {str(e)}"





# =====================================================
# IMAGE AI - CROP DISEASE DETECTION
# =====================================================

def detect_crop_disease(image):

    try:


        prompt = """

You are Agri AI Assist, an expert agricultural plant pathologist helping smallholder farmers in Uganda.


Analyze the crop image carefully.


Inspect:

• Leaves
• Fruits
• Stem
• Flowers
• Whole plant
• Visible insects
• Lesions
• Color changes
• Yellowing
• Spots
• Wilt
• Mold
• Rot
• Nutrient deficiency symptoms
• Pest damage



TASKS:


1. Identify the crop.


2. Determine whether the crop is:


Healthy

Diseased

Pest Damage

Nutrient Deficiency

Uncertain



3. If diseased:

Identify the MOST LIKELY disease.



4. If image quality is poor:

DO NOT guess.

Return:

"disease":"Uncertain"

"confidence":"Low"



------------------------------------------------

IMPORTANT:

Return ONLY valid JSON.

Never use markdown.

Never use ```json.

Never explain outside JSON.


------------------------------------------------


JSON FORMAT:


{
 "crop":"",
 "status":"",
 "disease":"",
 "confidence":"",
 "symptoms":"",
 "causes":"",
 "treatment":"",
 "recommendations":"",
 "prevention":""
}



------------------------------------------------


RULES:


Crop:

Return crop name only.


Examples:

Coffee

Maize

Tomato

Beans

Cassava

Banana

Rice

Groundnuts



------------------------------------------------


Status must be ONE of:


Healthy

Diseased

Pest Damage

Nutrient Deficiency

Uncertain



------------------------------------------------


Disease:


If healthy:

"Healthy"


If uncertain:

"Uncertain"


Otherwise:

Return disease name.



------------------------------------------------


Confidence:


Only:

High

Medium

Low



------------------------------------------------


Symptoms:


Describe visible symptoms briefly.



------------------------------------------------


Causes:


Explain possible cause.



------------------------------------------------


Treatment:


Give practical treatment advice.


Examples:


• Remove infected leaves.

• Apply recommended fungicide.

• Improve farm sanitation.

• Control pests.

• Improve soil nutrition.



------------------------------------------------


Recommendations:


Give smallholder farmer actions.



------------------------------------------------


Prevention:


Give future prevention tips.



------------------------------------------------


VERY IMPORTANT:


Never invent diseases.

If uncertain, say uncertain.


Return JSON ONLY.

"""



        response = model.generate_content(
            [
                prompt,
                image
            ]
        )


        return response.text



    except Exception as e:


        return json.dumps({

            "error": str(e)

        })






# =====================================================
# LUGANDA AGRICULTURAL EXPLANATION
# =====================================================


def generate_luganda_explanation(
        disease,
        crop,
        symptoms,
        causes,
        treatment,
        prevention
):


    try:


        prompt = f"""


You are Agri AI Assist helping Ugandan farmers.


Explain this crop disease in simple Luganda.


Crop:

{crop}



Disease:

{disease}



Symptoms:

{symptoms}



Causes:

{causes}



Treatment:

{treatment}



Prevention:

{prevention}





Write a farmer-friendly Luganda explanation containing:


1. Erinnya ly'obulwadde

2. Obubonero bw'obulwadde

3. Ensonga ezireeta obulwadde

4. Engeri y'okubujjanjaba

5. Engeri y'okubwetaasa



Use simple Luganda.

Avoid complicated scientific language.

Give practical advice farmers can follow.



"""


        response = model.generate_content(
            prompt
        )


        return response.text



    except Exception as e:


        return f"Luganda AI Error: {str(e)}"







# =====================================================
# SMART DIAGNOSIS REPORT
# =====================================================


def generate_smart_report(
        disease_json
):


    try:


        prompt = f"""


You are Agri AI Assist creating a professional crop diagnosis report for Ugandan farmers.


Disease information:


{disease_json}




Create:


Crop:

Disease:

Severity:
(Low / Medium / High)


Confidence:


Symptoms:


Cause:


Treatment:


Prevention:


Recovery timeline:


Estimated treatment cost in UGX:



Extension worker advice:




Make the report practical and easy for farmers to understand.



"""


        response = model.generate_content(
            prompt
        )


        return response.text



    except Exception as e:


        return f"Report Error: {str(e)}"






# =====================================================
# OPTIONAL JSON CLEANER
# Helps FastAPI parse Gemini responses safely
# =====================================================


def clean_json_response(response):


    try:

        cleaned = response.strip()


        if cleaned.startswith("```"):

            cleaned = cleaned.replace(
                "```json",
                ""
            )

            cleaned = cleaned.replace(
                "```",
                ""
            )


        return json.loads(cleaned)



    except Exception:


        return {

            "raw_response": response

        }
