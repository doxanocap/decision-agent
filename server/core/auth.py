"""
Authentication module.

Current: User ID from browser (localStorage)
Future: JWT validation from auth-api
"""

from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from server.core.config import config

# Security scheme (готово для JWT)
security = HTTPBearer(auto_error=False)


class AuthService:
    """
    Authentication service.
    
    MVP: Reads user_id from X-User-ID header (generated in browser)
    Future: Validates JWT and extracts user_id from auth-api
    """
    
    def __init__(self):
        # Fallback demo user (if header missing)
        self.demo_user_id = UUID("00000000-0000-0000-0000-000000000001")
    
    def get_current_user_id(
        self, 
        x_user_id: Optional[str] = Header(None),
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> UUID:
        """
        Get current user ID.
        
        MVP: Reads from X-User-ID header (browser-generated UUID)
        Future: Validates JWT token and extracts user_id
        
        Args:
            x_user_id: User ID from header (browser localStorage)
            credentials: Bearer token (optional for MVP)
            
        Returns:
            User UUID
            
        Raises:
            HTTPException: 401 if authentication fails (future)
        """
        # MVP: Read from header
        if x_user_id:
            try:
                return UUID(x_user_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user ID format"
                )
        
        # Fallback to demo user (for backward compatibility / testing)
        return self.demo_user_id
        
        # TODO: When integrating auth-api, uncomment below:
        # if not credentials:
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Not authenticated"
        #     )
        # return self._validate_jwt(credentials.credentials)
    
    def _validate_jwt(self, token: str) -> UUID:
        """
        Validate JWT token from auth-api.
        
        Future implementation:
        1. Decode JWT using shared secret
        2. Verify signature
        3. Check expiration
        4. Extract user_id from payload
        
        Args:
            token: JWT token string
            
        Returns:
            User UUID from token
            
        Raises:
            HTTPException: 401 if token is invalid
        """
        # TODO: Implement when integrating auth-api
        # import jwt
        # try:
        #     payload = jwt.decode(
        #         token,
        #         config.JWT_SECRET_KEY,
        #         algorithms=["HS256"]
        #     )
        #     user_id = payload.get("user_id") or payload.get("sub")
        #     if not user_id:
        #         raise HTTPException(status_code=401, detail="Invalid token")
        #     return UUID(user_id)
        # except jwt.ExpiredSignatureError:
        #     raise HTTPException(status_code=401, detail="Token expired")
        # except jwt.InvalidTokenError:
        #     raise HTTPException(status_code=401, detail="Invalid token")
        
        raise NotImplementedError("JWT validation not implemented yet")


# Singleton instance
_auth_service = AuthService()


def get_current_user(
    x_user_id: Optional[str] = Header(None),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UUID:
    """
    Dependency for getting current user ID.
    
    Use this in route handlers:
        @router.post("/endpoint")
        async def endpoint(user_id: UUID = Depends(get_current_user)):
            ...
    """
    return _auth_service.get_current_user_id(x_user_id, credentials)
