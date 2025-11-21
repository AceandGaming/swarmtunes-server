from .database import BaseDatabase
import scripts.paths as paths
from scripts.serializer import TokenSerializer
from scripts.types import Token

class TokenDatabase(BaseDatabase[Token]):
    def __init__(self):
        super().__init__(Token, TokenSerializer, paths.TOKENS_DIR)