from fastapi import APIRouter
from schemas import QuestionRequest
from database import supabase
from ai_service import ask_gemini

router = APIRouter()


@router.post("/ask-ai")
async def ask_ai(data: QuestionRequest):

    question = data.question

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
    # DEBUG (TEMP - REMOVE LATER)
    # =========================
    print("ROWS COUNT:", len(rows))
    print("KB SAMPLE:", rows[:2])

    # =========================
    # STEP 2: IMPROVED AGRI INTELLIGENT FILTER (FIXED)
    # =========================

    question_words = set(question.lower().replace(",", "").split())

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

        # match if ANY keyword is found anywhere in row text
        if any(word in text for word in question_words):
            relevant_rows.append(r)

    # fallback (IMPORTANT SAFETY NET)
    use_rows = relevant_rows if relevant_rows else rows[:5]

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
        knowledge_text = "NO LOCAL KNOWLEDGE FOUND."

    # =========================
    # STEP 4: HYBRID GEMINI PROMPT (RAG + LLM)
    # =========================
    prompt = f"""
You are Agri AI Assist, a smart farming assistant.

You are given agricultural knowledge from a local database and general agronomy knowledge.

RULES:
- Always prioritize LOCAL KNOWLEDGE first
- Use it if relevant
- If incomplete, expand using general agronomy knowledge
- Be practical and farmer-friendly

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
- Simple and actionable
- Use bullet points if needed
- Avoid long theory
"""

    # =========================
    # STEP 5: CALL GEMINI
    # =========================
    answer = ask_gemini(prompt)

    return {
        "question": question,
        "answer": answer
        }
