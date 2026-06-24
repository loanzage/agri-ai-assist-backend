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
    # BUILD KNOWLEDGE TEXT
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
        knowledge_text = "NO KNOWLEDGE BASE DATA FOUND."

    # =========================
    # STRICT GEMINI PROMPT
    # =========================
    prompt = f"""
You are Agri AI Assist.

YOU MUST FOLLOW THESE RULES STRICTLY:

1. Use ONLY the knowledge base below if it contains relevant information.
2. If the knowledge base contains relevant information, prioritize it.
3. If the knowledge base is empty or irrelevant, use general agronomy knowledge.
4. Do NOT ignore the knowledge base.

====================
KNOWLEDGE BASE (TRUST THIS FIRST)
====================
{knowledge_text}

====================
QUESTION
====================
{question}

====================
RESPONSE RULES:
- Keep answer simple and actionable
- Farmer-friendly language
- Do NOT mention "based on general knowledge" unless KB is empty
"""

    # =========================
    # CALL AI
    # =========================
    answer = ask_gemini(prompt)

    return {
        "question": question,
        "answer": answer
    }
