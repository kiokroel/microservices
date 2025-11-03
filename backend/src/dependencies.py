import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Получить текущего аутентифицированного пользователя через users_api"""
    token = credentials.credentials
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "http://users-api:8000/api/users/me",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        if resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Неверный токен или пользователь не найден"
            )
        
        return resp.json()
    except httpx.RequestError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис аутентификации недоступен"
        )
