import uuid
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class User:
    """
    Data model for a user
    """
    id: uuid.UUID
    username: str
    password: str  # hashed password
    email: str
    is_active: bool = True
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        if isinstance(data.get('id'), str):
            data['id'] = uuid.UUID(data['id'])
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': str(self.id),
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def to_public_dict(self) -> Dict[str, Any]:
        """Returns user data without sensitive information"""
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }