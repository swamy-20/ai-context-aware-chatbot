from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List

from pipeline import NLPPipeline

class ChatRequest(BaseModel):
    message: str
    context: List[Dict[str, str]] = []

app = FastAPI()
pipeline = NLPPipeline()

@app.post('/process')
async def process_chat(payload: ChatRequest):
    analysis = pipeline.process(payload.message, payload.context)
    return analysis
