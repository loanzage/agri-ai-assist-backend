from fastapi import APIRouter
from schemas import QuestionRequest
from database import supabase
from ai_service import ask_gemini

router = APIRouter()


@router.post("/ask-ai")
async def ask_ai(data: QuestionRequest):

    question = data.question

    # =========================
    # FETCH KNOWLEDGE BASE
    # =========================

    # OPTION 1: Get ALL crops (recommended for now)
    kb_response = (
        supabase
        .table("knowledge_base")
        .select("*")
        .execute()
    )

    # OPTION 2 (UNCOMMENT if you want maize-only filtering)
    """
    kb_response = (
        supabase
        .table("knowledge_base")
        .select("*")
        .eq("category", "maize")
        .execute()
    )
    """

    rows = kb_response.data or []

    # =========================
    # BUILD KNOWLEDGE TEXT
    # =========================

    knowledge_text = ""

    for row in rows:
        knowledge_text += f"""
Crop: {row.get('crop')}
Topic: {row.get('topic')}
Trigger: {row.get('trigger')}
Causes: {row.get('causes_or_details')}
Recommendations: {row.get('recommendations')}
Risk: {row.get('risk_level')}
---
"""

    # If DB is empty, force fallback text (IMPORTANT FIX)
    if not knowledge_text.strip():
        knowledge_text = "No local knowledge base found. Use general agricultural knowledge."

    # =========================
    # BUILD GEMINI PROMPT
    # =========================

    prompt = f"""
You are Agri AI Assist.

You MUST use the agricultural knowledge below if relevant:

{knowledge_text}

QUESTION:
{question}

Instructions:
- Give a clear practical farming answer
- If knowledge is available, prioritize it
- If not, use general agronomy knowledge
- Be simple and farmer-friendly
"""

    # =========================
    # CALL GEMINI
    # =========================

    answer = ask_gemini(prompt)

    return {
        "question": question,
        "answer": answer
    }
