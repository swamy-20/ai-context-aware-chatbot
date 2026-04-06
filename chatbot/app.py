from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import os
import uvicorn
import math

# Import custom modules
from preprocessing.tokenizer import tokenize_text
from preprocessing.lemmatizer import lemmatize_text
from nlp_modules.ner import extract_entities
from nlp_modules.dependency_parser import parse_dependencies
from nlp_modules.coreference import resolve_coreferences
from context.memory import context_manager
from response.generator import generator
from embeddings.word2vec import train_or_load_w2v
from intent.ngrams import train_ngram

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI-Based Intelligent Context-Aware Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows HTML frontend to fetch API locally
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    level: int = 3 # 1, 2, or 3 for response generation level
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Hello there! How are you?",
                "session_id": "default",
                "level": 3
            }
        }
    }

# Setup dataset path
DATASET_PATH = os.path.join(os.path.dirname(__file__), "dataset", "chatbot_conversations.csv")

# Global Error Handler for Invalid JSON / Formatting
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Please send data in JSON format. Your input might be plain text or missing quotes."},
    )

@app.on_event("startup")
async def startup_event():
    # Pre-load trained models in the same process so generator.is_trained is True.
    if os.path.exists(DATASET_PATH):
        print("Dataset found. Loading and training models...")
        generator.load_and_train(DATASET_PATH)
        train_or_load_w2v(DATASET_PATH)
        train_ngram(DATASET_PATH)
        print("Models loaded and ready.")
    else:
        print("Warning: Dataset not found. Please place chatbot_conversations.csv in dataset folder.")

@app.get("/")
async def get_ui():
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    session_id = request.session_id
    raw_message = request.message
    
    # Context Management: Retrieve history & replace pronouns
    ctx = context_manager.get_context(session_id)
    resolved_message = resolve_coreferences(raw_message, ctx.entities)
    
    # Preprocessing
    tokens, clean_tokens = tokenize_text(resolved_message)
    lemmas = lemmatize_text(resolved_message)
    
    # NLP Modules
    entities = extract_entities(resolved_message)
    
    # Intent/Context update
    context_manager.update_history(session_id, "user", raw_message)
    if entities:
        context_manager.add_entities(session_id, entities)
        
    # Assume intent is basic context from token features
    predicted_intent = clean_tokens[0] if clean_tokens else "unknown"
    
    # Generate Response based on requested level
    reply = ""
    similarity_score = 0.0
    
    try:
        if request.level == 1:
            reply, similarity_score, predicted_intent = generator.level_1_tfidf(resolved_message)
        elif request.level == 2:
            reply, similarity_score, predicted_intent = generator.level_2_w2v(resolved_message)
        else:
            reply, similarity_score, predicted_intent = generator.level_3_hybrid(resolved_message)
    except Exception as e:
        reply = f"Error generating response: {str(e)}"
        
    context_manager.update_history(session_id, "bot", reply)
    
    return {
        "reply": reply,
        "resolved_query": resolved_message,
        "tokens": tokens,
        "lemmas": lemmas,
        "entities": entities,
        "intent": predicted_intent,
        "similarity_score": similarity_score,
        "level_used": request.level
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=False)
