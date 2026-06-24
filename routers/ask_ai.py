from fastapi import APIRouter
from schemas import QuestionRequest
from database import supabase
from ai_service import ask_gemini

router = APIRouter()


@router.post("/ask-ai")
async def ask_ai(data: QuestionRequest):

    # ✅ FIX: proper indentation (THIS WAS YOUR CRASH)
    question = data.question

    # Search knowledge base first
    kb_response = (
        supabase
        .table("knowledge_base")
        .select("*")
        .execute()
    )

    knowledge_text = ""

    if kb_response.data:
        for row in kb_response.data:
            knowledge_text += f"""
Crop: {row.get('crop')}
Topic: {row.get('topic')}
Details: {row.get('causes_or_details')}
Recommendations: {row.get('recommendations')}
Risk: {row.get('risk_level')}
"""

    prompt = f"""
You are Agri AI Assist.

Use the agricultural knowledge below to answer the farmer.

KNOWLEDGE:
{knowledge_text}

QUESTION:
{question}

Provide a practical farming answer.
"""

    answer = ask_gemini(prompt)

    return {
        "question": question,
        "answer": answer
    }
