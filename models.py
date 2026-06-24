from pydantic import BaseModel

class Farmer(BaseModel):
id: int
user_id: str
name: str
region: str
farm_size: float
crops: str

class KnowledgeBase(BaseModel):
id: int
category: str
crop: str
topic: str
trigger: str
causes_or_details: str
recommendations: str
risk_level: str
source_dataset: str

class MarketPrice(BaseModel):
id: int
crop: str
district: str
price: float
date_recorded: str

class WeatherAlert(BaseModel):
id: int
district: str
alert_type: str
advisory: str

class ChatHistory(BaseModel):
id: int
farmer_id: int
question: str
answer: str