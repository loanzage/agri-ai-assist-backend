from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str


class AIResponse(BaseModel):
    question: str
    answer: str


class FarmerCreate(BaseModel):
    name: str
    region: str
    farm_size: float
    crops: str


class ChatMessage(BaseModel):
    farmer_id: int
    question: str
    answer: str
