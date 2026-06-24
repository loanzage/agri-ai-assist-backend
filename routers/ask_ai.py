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
    # STEP 2: FILTER RELEVANT KB (IMPORTANT FIX)
    # =========================
    relevant_rows = [
        r for r in rows
        if question.lower() in (
            str(r.get("crop", "")) +
            str(r.get("topic", "")) +
            str(r.get("trigger", ""))
        ).lower()
    ]

    use_rows = relevant_rows if relevant_rows else rows[:5]

    # =========================
    # DEBUG (TEMP - REMOVE LATER)
    # =========================
    print("ROWS COUNT:", len(rows))
    print("RELEVANT ROWS:", len(relevant_rows))
    print("KB SAMPLE:", rows[:2])

    # =========================
    # STEP 3: BUILD KNOWLEDGE CONTEXT
    # =========================
    knowledge_text = ""

    for r in use_rows:
        knowledge_text += f"""
Crop: {r.get('crop')}
Topic: {r.get('topic')}
Cause: {r.get('causes_or_details')}
Recommendation: {r.get('recommendations')}
Risk: {r.get('risk_level')}
---
"""

    if not knowledge_text.strip():
        knowledge_text = "NO LOCAL KNOWLEDGE BASE FOUND."

    # =========================
    # STEP 4: HYBRID RAG + GEMINI PROMPT
    # =========================
    prompt = f"""
You are Agri AI Assist.

You MUST follow these rules:

- Use ONLY the knowledge base if relevant
- Do NOT ignore knowledge base facts
- If knowledge base is relevant, prioritize it first
- If knowledge base is weak or incomplete, then expand using general agronomy knowledge

====================
KNOWLEDGE BASE
====================
{knowledge_text}

====================
QUESTION
====================
{question}

RESPONSE RULES:
- Be simple and practical
- Use bullet points if helpful
- Avoid long theory
- Focus on actionable farming advice
"""

    # =========================
    # STEP 5: CALL GEMINI
    # =========================
    answer = ask_gemini(prompt)

    return {
        "question": question,
        "answer": answer
    }
