from pydantic import BaseModel
from typing import List, Dict

class ChatContext(BaseModel):
    session_id: str
    history: List[Dict[str, str]] = []
    entities: List[Dict[str, str]] = []
    last_intent: str | None = None
    
class ContextManager:
    def __init__(self):
        self.sessions = {} # session_id -> ChatContext
        
    def get_context(self, session_id: str = "default") -> ChatContext:
        if session_id not in self.sessions:
            self.sessions[session_id] = ChatContext(session_id=session_id)
        return self.sessions[session_id]
        
    def update_history(self, session_id: str, role: str, message: str):
        ctx = self.get_context(session_id)
        ctx.history.append({"role": role, "content": message})
        
    def add_entities(self, session_id: str, new_entities: list):
        ctx = self.get_context(session_id)
        ctx.entities.extend(new_entities)
        if len(ctx.entities) > 20:
            ctx.entities = ctx.entities[-20:]
            
    def set_intent(self, session_id: str, intent: str):
        ctx = self.get_context(session_id)
        ctx.last_intent = intent

context_manager = ContextManager()
