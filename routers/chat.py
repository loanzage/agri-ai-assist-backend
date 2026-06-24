from fastapi import APIRouter
from database import supabase
from schemas import ChatMessage

router = APIRouter()

Get all chat history

@router.get("/chat-history")
async def get_chat_history():

response = (
    supabase
    .table("chat_history")
    .select("*")
    .order("id", desc=True)
    .execute()
)

return response.data

Get chat history for one farmer

@router.get("/chat-history/{farmer_id}")
async def get_farmer_chat_history(farmer_id: int):

response = (
    supabase
    .table("chat_history")
    .select("*")
    .eq("farmer_id", farmer_id)
    .order("id", desc=True)
    .execute()
)

return response.data

Save a chat message

@router.post("/chat-history")
async def save_chat_message(data: ChatMessage):

response = (
    supabase
    .table("chat_history")
    .insert({
        "farmer_id": data.farmer_id,
        "question": data.question,
        "answer": data.answer
    })
    .execute()
)

return response.data
