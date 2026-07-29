from fastapi import APIRouter

from schemas import QuestionRequest

from database import supabase

from ai_service import ask_gemini



router = APIRouter()





@router.post("/ask-ai")
async def ask_ai(data: QuestionRequest):


    question = data.question

    language = data.language



    # =========================
    # STEP 1: FETCH SUPABASE KNOWLEDGE (RAG)
    # =========================

    kb_response = (

        supabase

        .table("knowledge_base")

        .select("*")

        .execute()

    )


    rows = kb_response.data or []





    # =========================
    # DEBUG
    # =========================

    print("ROWS COUNT:", len(rows))

    print("LANGUAGE:", language)

    print("KB SAMPLE:", rows[:2])







    # =========================
    # STEP 2: AGRI KNOWLEDGE FILTER
    # =========================


    question_words = set(
        question.lower()
        .replace(",", "")
        .split()
    )



    def row_text(r):

        return " ".join([

            str(r.get("crop", "")),

            str(r.get("topic", "")),

            str(r.get("trigger", "")),

            str(r.get("causes_or_details", "")),

            str(r.get("recommendations", ""))

        ]).lower()





    relevant_rows = []



    for r in rows:


        text = row_text(r)


        if any(word in text for word in question_words):

            relevant_rows.append(r)







    # fallback

    use_rows = (
        relevant_rows
        if relevant_rows
        else rows[:5]
    )







    # =========================
    # STEP 3: BUILD KNOWLEDGE CONTEXT
    # =========================


    knowledge_text = ""



    for r in use_rows:


        knowledge_text += f"""

Crop: {r.get('crop')}

Topic: {r.get('topic')}

Trigger: {r.get('trigger')}

Causes: {r.get('causes_or_details')}

Recommendations: {r.get('recommendations')}

Risk: {r.get('risk_level')}

---

"""




    if not knowledge_text.strip():

        knowledge_text = (
            "NO LOCAL KNOWLEDGE FOUND."
        )







    # =========================
    # STEP 4: MULTILINGUAL GEMINI PROMPT
    # =========================


    prompt = f"""

You are Agri AI Assist,
a smart farming assistant for farmers in Uganda.



IMPORTANT LANGUAGE RULE:

Answer the farmer ONLY in:

{language}



Use simple farmer-friendly language.



RULES:

- Always prioritize LOCAL KNOWLEDGE first.

- Use local knowledge when relevant.

- If incomplete, add general agronomy knowledge.

- Give practical farming advice.

- Avoid unnecessary scientific explanations.



====================

LOCAL KNOWLEDGE BASE

====================

{knowledge_text}



====================

FARMER QUESTION

====================

{question}



====================

RESPONSE STYLE:

- Simple and actionable.

- Use bullet points where helpful.

- Include practical steps.

- Be suitable for smallholder farmers.

"""







    # =========================
    # STEP 5: CALL GEMINI
    # =========================


    answer = ask_gemini(prompt)



    return {


        "question": question,


        "language": language,


        "answer": answer


    }
