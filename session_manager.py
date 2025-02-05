import uuid
from datetime import datetime

class SessionManager:
    def __init__(self):
        self.active_sessions = {}
        
    def create_session(self, email):
        """创建新会话"""
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = {
            'email': email,
            'created_at': datetime.now(),
            'last_active': datetime.now()
        }
        return session_id 