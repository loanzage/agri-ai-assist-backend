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
# IMAGE AI - SMART CROP DISEASE DETECTION
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


====================================================

TASKS

Identify:

1. Crop name

2. Plant health status

Choose one:

Healthy
Diseased
Pest Damage
Nutrient Deficiency
Uncertain


3. If diseased:

Identify the most likely disease.


4. If the image is unclear:

DO NOT guess.

Return:

"disease":"Uncertain"

"confidence":"Low"


====================================================

IMPORTANT JSON RULES

Return ONLY valid JSON.

Never use markdown.

Never use ```json.

Never explain outside JSON.


====================================================

JSON FORMAT


{
"crop":"",
"status":"",
"disease":"",
"confidence":"",
"severity":"",
"symptoms":"",
"causes":"",
"treatment":"",
"prevention":"",
"recovery_time":"",
"estimated_cost":""
}


====================================================


FIELD RULES


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



----------------------------------------------------


Status:

Must be one of:

Healthy

Diseased

Pest Damage

Nutrient Deficiency

Uncertain



----------------------------------------------------


Disease:


If healthy:

"Healthy"


If uncertain:

"Uncertain"


Otherwise:

Return disease name.



----------------------------------------------------


Confidence:

Only:

High

Medium

Low



----------------------------------------------------


Severity:

Estimate disease seriousness.

Only:

Low

Medium

High



----------------------------------------------------


Symptoms:

Describe visible symptoms.

Example:

Yellow spots on leaves, leaf drying, reduced growth.



----------------------------------------------------


Causes:

Explain possible causes.

Example:

Fungal infection caused by high humidity and poor airflow.



----------------------------------------------------


Treatment:

Explain what the farmer should do now.

Include:

- Safe farming practices
- Disease control methods
- Possible farm actions


Examples:

Remove infected leaves.

Apply recommended fungicide.

Improve farm sanitation.

Control pests.

Improve soil nutrition.



----------------------------------------------------


Prevention:

Explain how to avoid the disease in future seasons.

Include:

Crop management tips.

Field hygiene.

Early monitoring.



----------------------------------------------------


Recovery_time:

Estimate how long improvement may take.


Examples:

1-2 weeks

2-4 weeks

One growing season



----------------------------------------------------


Estimated_cost:

Give approximate Uganda farmer costs.


Examples:

UGX 20,000 - 50,000 per acre


If unknown:

"Consult local agro-input supplier"



====================================================


VERY IMPORTANT:

Never invent diseases.

If uncertain:

Return:

"disease":"Uncertain"

"confidence":"Low"


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

You are Agri AI Assist helping farmers in Uganda.

Explain this crop disease in simple Luganda language.


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



Create a farmer-friendly explanation.


Include:


1. Erinnya ly'obulwadde


2. Obubonero bw'obulwadde


3. Ensonga ezireeta obulwadde


4. Engeri y'okubujjanjaba


5. Engeri y'okubwetaasa


6. Obudde ekimera bwe kiyinza okutereera



Instructions:

Use simple Luganda.

Avoid difficult scientific words.

Give practical advice farmers can follow.

"""


        response = model.generate_content(
            prompt
        )


        return response.text



    except Exception as e:

        return f"Luganda AI Error: {str(e)}"







# =====================================================
# SMART DIAGNOSIS REPORT GENERATOR
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


🌾 Crop:


🐛 Disease:


⚠ Severity:


📈 Confidence:


📋 Symptoms:


⚠ Cause:


💊 Treatment:


🌱 Prevention:


⏳ Recovery timeline:


💰 Estimated treatment cost in UGX:


👨🏾‍🌾 Extension worker advice:



Make the report:

- Practical
- Easy to understand
- Suitable for smallholder farmers in Uganda


"""


        response = model.generate_content(
            prompt
        )


        return response.text



    except Exception as e:


        return f"Report Error: {str(e)}"







# =====================================================
# JSON CLEANER
# =====================================================

def clean_json_response(response):

    try:

        cleaned = response.strip()


        cleaned = (
            cleaned
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )


        return json.loads(cleaned)



    except Exception:


        return {

            "raw_response": response

        }
