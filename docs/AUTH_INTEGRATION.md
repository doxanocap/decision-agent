# Auth Integration Guide

## Current State (MVP)

Сейчас используется **hardcoded demo user**:
- `user_id = "00000000-0000-0000-0000-000000000001"`
- Все запросы работают без токена
- Данные изолированы по `user_id` в БД

## Future: Integrating with auth-api

### Step 1: Shared Secret

В обоих сервисах должен быть **одинаковый** `JWT_SECRET_KEY`:

```bash
# auth-api/.env
JWT_SECRET_KEY=your-super-secret-key-12345

# decisions/.env  
JWT_SECRET_KEY=your-super-secret-key-12345  # ← ТОТ ЖЕ!
```

### Step 2: Enable JWT Validation

В `server/core/auth.py` раскомментировать код:

```python
def get_current_user_id(
    self, 
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UUID:
    # UNCOMMENT THIS:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return self._validate_jwt(credentials.credentials)
    
    # REMOVE THIS:
    # return self.demo_user_id
```

И раскомментировать `_validate_jwt`:

```python
def _validate_jwt(self, token: str) -> UUID:
    import jwt
    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        user_id = payload.get("user_id") or payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return UUID(user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Step 3: Install PyJWT

```bash
pip install pyjwt
```

### Step 4: Frontend Changes

```javascript
// Login через auth-api
const login = async (email, password) => {
  const response = await axios.post('http://auth-api-url/auth/login', {
    email,
    password
  });
  
  const { access_token } = response.data;
  localStorage.setItem('token', access_token);
};

// Axios interceptor (уже готов в api.js, просто раскомментировать)
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Step 5: Test

1. Запусти auth-api
2. Залогинься через auth-api → получи JWT
3. Используй JWT в decisions API
4. Проверь что `user_id` извлекается из токена

## Architecture After Integration

```
Frontend
   │
   │ 1. Login
   ├──────────────► auth-api (Go)
   │ ◄──────────────┤ {access_token}
   │
   │ 2. Analyze Decision
   │    Authorization: Bearer <token>
   ├──────────────► decisions-api (Python)
   │                │
   │                │ Validates JWT
   │                │ Extracts user_id
   │                │ Filters by user_id
   │ ◄──────────────┤
```

## Migration Notes

- Существующие данные уже привязаны к demo user
- Новые пользователи получат свои `user_id` из JWT
- Данные изолированы - каждый видит только свои решения

## Rollback

Если что-то пойдет не так, просто закомментируй обратно:

```python
# В server/core/auth.py
def get_current_user_id(...):
    return self.demo_user_id  # ← Вернуть hardcoded
```

Все endpoints уже готовы, просто переключаешь источник `user_id`.
