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
    # STEP 2: BUILD KNOWLEDGE CONTEXT
    # =========================
    knowledge_text = ""

    for r in rows:
        knowledge_text += f"""
Crop: {r.get('crop', 'N/A')}
Topic: {r.get('topic', 'N/A')}
Trigger: {r.get('trigger', 'N/A')}
Causes: {r.get('causes_or_details', 'N/A')}
Recommendations: {r.get('recommendations', 'N/A')}
Risk: {r.get('risk_level', 'N/A')}
---
"""

    if not knowledge_text.strip():
        knowledge_text = "NO LOCAL KNOWLEDGE BASE FOUND."

    # =========================
    # STEP 3: HYBRID GEMINI PROMPT (RAG + LLM)
    # =========================
    prompt = f"""
You are Agri AI Assist, a smart farming assistant.

You are given TWO sources of knowledge:

1. LOCAL KNOWLEDGE BASE (trusted farming data from Uganda/region)
2. YOUR GENERAL AGRONOMY KNOWLEDGE (global farming science)

RULES:
- ALWAYS prioritize LOCAL KNOWLEDGE BASE first
- If local knowledge is incomplete, use general knowledge to expand
- Combine both when needed
- Never ignore local knowledge if relevant

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
- Simple, practical, farmer-friendly
- Step-by-step if possible
- Avoid long theory
"""

    # =========================
    # STEP 4: CALL GEMINI
    # =========================
    answer = ask_gemini(prompt)

    return {
        "question": question,
        "answer": answer
    }
