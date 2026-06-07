from fastapi import Depends, HTTPException, status
from typing import Annotated
from fastapi import security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_api_key(token: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> str:
    """Extracts the raw API key from the Authorization Bearer header."""
    authorization = token.credentials
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
    
    api_key = authorization.split(" ", 1)[1].strip()
    return api_key