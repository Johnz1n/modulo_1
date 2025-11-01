from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path
import json

from ..models.user import User


class UserRepositoryInterface(ABC):
    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[User]:
        pass


class UserRepository(UserRepositoryInterface):
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.users_file = data_dir / "users.json"
    
    def _load_users_data(self) -> List[User]:
        if not self.users_file.exists():
            return []
        
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users_data = json.load(f)

        return [User.from_dict(user) for user in users_data]
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        users = self._load_users_data()
        for user in users:
            if user.username == username:
                return user
        return None
