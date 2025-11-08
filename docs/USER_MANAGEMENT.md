# User Management - Documentación Completa

## Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Arquitectura](#arquitectura)
3. [Flujos de Negocio](#flujos-de-negocio)
4. [Componentes por Capa](#componentes-por-capa)
5. [Modelos de Datos](#modelos-de-datos)
6. [APIs y Endpoints](#apis-y-endpoints)
7. [Seguridad](#seguridad)
8. [Casos de Uso](#casos-de-uso)

---

## Visión General

El módulo de User Management implementa un sistema completo de autenticación y gestión de usuarios siguiendo los principios de **Clean Architecture** y **Domain-Driven Design (DDD)**.

### Características Principales

- ✅ Registro de usuarios con validación de datos
- ✅ Autenticación mediante JWT (JSON Web Tokens)
- ✅ Hash seguro de contraseñas con bcrypt
- ✅ Gestión de estados de usuario (activo/inactivo, verificado/no verificado)
- ✅ Validación de unicidad de email y username
- ✅ API RESTful con FastAPI
- ✅ Persistencia asíncrona con SQLAlchemy + PostgreSQL

---

## Arquitectura

El sistema está organizado en 4 capas siguiendo Clean Architecture:

```
┌─────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                    │
│              (FastAPI, Pydantic Schemas)                │
├─────────────────────────────────────────────────────────┤
│                 INFRASTRUCTURE LAYER                    │
│        (SQLAlchemy, Bcrypt, JWT, PostgreSQL)            │
├─────────────────────────────────────────────────────────┤
│                  APPLICATION LAYER                      │
│              (Use Cases, DTOs, Interfaces)              │
├─────────────────────────────────────────────────────────┤
│                    DOMAIN LAYER                         │
│         (Entities, Value Objects, Repositories)         │
└─────────────────────────────────────────────────────────┘
```

### Principios de Diseño

1. **Dependency Inversion**: Las capas externas dependen de las internas
2. **Separation of Concerns**: Cada capa tiene responsabilidades específicas
3. **Single Responsibility**: Cada componente tiene una única razón para cambiar
4. **Open/Closed**: Abierto a extensión, cerrado a modificación

---

## Flujos de Negocio

### 1. Flujo de Registro de Usuario

```
┌─────────┐      ┌───────────┐      ┌──────────────┐      ┌─────────┐
│ Cliente │─────▶│   API     │─────▶│  Use Case    │─────▶│   Hash  │
└─────────┘      │ /register │      │ RegisterUser │      │ Service │
                 └───────────┘      └──────────────┘      └─────────┘
                                           │
                                           ▼
                                   ┌──────────────┐
                                   │ User Entity  │
                                   │  (Domain)    │
                                   └──────────────┘
                                           │
                                           ▼
                                   ┌──────────────┐      ┌──────────┐
                                   │  Repository  │─────▶│ Database │
                                   └──────────────┘      └──────────┘
```

**Pasos**:

1. Cliente envía datos (email, password, username)
2. Pydantic valida el formato de los datos
3. Use Case valida unicidad de email/username
4. Hash Service hashea la contraseña con bcrypt
5. Se crea la entidad User en el dominio
6. Repository persiste en la base de datos
7. Se retorna UserResponseDTO al cliente

### 2. Flujo de Login

```
┌─────────┐      ┌──────────┐      ┌─────────────┐      ┌──────────┐
│ Cliente │─────▶│   API    │─────▶│  Use Case   │─────▶│   Hash   │
└─────────┘      │  /login  │      │  LoginUser  │      │ Service  │
                 └──────────┘      └─────────────┘      └──────────┘
                                            │                  │
                                            ▼                  │
                                    ┌──────────────┐           │
                                    │  Repository  │           │
                                    │ find_by_email│           │
                                    └──────────────┘           │
                                            │                  │
                                            ▼                  │
                                    Verificar password◀────────┘
                                            │
                                            ▼
                                    ┌──────────────┐
                                    │    Token     │
                                    │   Service    │
                                    └──────────────┘
```

**Pasos**:

1. Cliente envía email y password
2. Repository busca usuario por email
3. Hash Service verifica la contraseña
4. Se valida que el usuario esté activo
5. Token Service genera un JWT
6. Se retorna el token al cliente

### 3. Flujo de Autenticación (Obtener Usuario Actual)

```
┌─────────┐      ┌──────────┐      ┌────────────────┐      ┌──────────┐
│ Cliente │─────▶│   API    │─────▶│ Dependency     │─────▶│  Token   │
│ +Token  │      │   /me    │      │get_current_user│      │ Service  │
└─────────┘      └──────────┘      └────────────────┘      └──────────┘
                                            │                  │
                                            │                  │
                                            │        Validar ──┘
                                            │        Token
                                            ▼
                                    ┌──────────────┐
                                    │  Repository  │
                                    │ find_by_id   │
                                    └──────────────┘
                                            │
                                            ▼
                                       User Entity
```

**Pasos**:

1. Cliente envía request con header `Authorization: Bearer <token>`
2. Dependency `get_current_user` extrae el token
3. Token Service valida y decodifica el JWT
4. Repository busca usuario por ID del token
5. Se retorna el User Entity

---

## Componentes por Capa

### 📦 Domain Layer (`app/domain/`)

#### Entities (`entities/`)

**`base.py`** - Entidad base con campos comunes

```python
class BaseEntity:
    - id: UUID
    - created_at: datetime
    - updated_at: datetime
```

**`user.py`** - Entidad principal de usuario

```python
class User(BaseEntity):
    - _email: Email (Value Object)
    - _hashed_password: HashedPassword (Value Object)
    - _username: str
    - _is_active: bool
    - _is_verified: bool

    Métodos:
    - update_email(email: Email)
    - update_password(hashed_password: HashedPassword)
    - update_username(username: str)
    - activate() / deactivate()
    - verify_email()
```

#### Value Objects (`value_objects/`)

**`email.py`** - Validación de email

```python
class Email:
    - Validación con regex RFC 5322
    - Normalización a lowercase
    - Máximo 255 caracteres
    - Inmutable
```

**`password.py`** - Validación de contraseñas

```python
class PlainPassword:
    - Mínimo 8 caracteres
    - Máximo 72 caracteres (límite bcrypt)
    - No se expone en __str__ (seguridad)

class HashedPassword:
    - Mínimo 59 caracteres (formato bcrypt)
    - No se expone en __str__ (seguridad)
```

#### Repositories (`repositories/`)

**`user_repository.py`** - Interfaz abstracta

```python
class UserRepository(ABC):
    - save(user: User) -> User
    - find_by_id(user_id: UUID) -> User | None
    - find_by_email(email: str) -> User | None
    - find_by_username(username: str) -> User | None
    - update(user: User) -> User
    - delete(user_id: UUID) -> None
    - exists_by_email(email: str) -> bool
    - exists_by_username(username: str) -> bool
    - list_all(skip: int, limit: int) -> list[User]
    - count() -> int
```

#### Exceptions (`exceptions/`)

**`user_exceptions.py`** - Excepciones del dominio

```python
- UserDomainError (base)
- UserNotFoundError
- UserAlreadyExistsError
- InvalidCredentialsError
- UserNotActiveError
- UserNotVerifiedError
- InvalidPasswordError
- InvalidUsernameError
- InvalidEmailError
```

---

### 🔧 Application Layer (`app/application/`)

#### DTOs (`dtos/`)

**`auth_dtos.py`** - Data Transfer Objects

```python
@dataclass(frozen=True)
class RegisterUserDTO:
    email: str
    password: str
    username: str

@dataclass(frozen=True)
class LoginDTO:
    email: str
    password: str

@dataclass(frozen=True)
class TokenDTO:
    access_token: str
    token_type: str
    expires_at: datetime | None

@dataclass(frozen=True)
class UserResponseDTO:
    id: str
    email: str
    username: str
    is_active: bool
    is_verified: bool
    created_at: datetime
```

#### Use Cases (`use_cases/auth/`)

**`register_user.py`** - Caso de uso de registro

```python
class RegisterUser:
    Responsabilidades:
    - Validar que email no exista
    - Validar que username no exista
    - Crear Email value object
    - Hashear contraseña (PlainPassword → HashedPassword)
    - Crear User entity
    - Persistir usuario
    - Retornar UserResponseDTO
```

**`login_user.py`** - Caso de uso de login

```python
class LoginUser:
    Responsabilidades:
    - Buscar usuario por email
    - Verificar contraseña
    - Validar que usuario esté activo
    - Generar JWT token
    - Retornar TokenDTO con token y expiración
```

#### Interfaces (`interfaces/`)

**`hash_service.py`** - Abstracción de hashing

```python
class HashService(ABC):
    def hash_password(password: str) -> str
    def verify_password(password: str, hashed: str) -> bool
```

**`token_service.py`** - Abstracción de tokens

```python
class TokenService(ABC):
    def generate_token(user_id: str, email: str) -> str
    def validate_token(token: str) -> dict
    def get_token_expiration(token: str) -> datetime
```

---

### 🗄️ Infrastructure Layer (`app/infrastructure/`)

#### Database (`database/`)

**`models.py`** - Modelo SQLAlchemy

```python
class UserModel(Base):
    __tablename__ = "users"

    id: UUID (primary key)
    email: String(255) (unique, indexed)
    hashed_password: String(255)
    username: String(50) (unique, indexed)
    is_active: Boolean (default=True)
    is_verified: Boolean (default=False)
    created_at: DateTime
    updated_at: DateTime
```

**`config.py`** - Configuración de base de datos

```python
class DatabaseConfig:
    - engine: AsyncEngine (PostgreSQL)
    - session_maker: async_sessionmaker
    - create_tables()
    - drop_tables()
    - close()
```

#### Repositories (`repositories/`)

**`user_repository.py`** - Implementación SQLAlchemy

```python
class SQLAlchemyUserRepository(UserRepository):
    - Implementa toda la interfaz UserRepository
    - Conversiones: Entity ↔ Model
    - Manejo de transacciones async
    - Manejo de excepciones SQLAlchemy → Domain
```

#### Services (`services/`)

**`hash_service.py`** - Implementación con bcrypt

```python
class BcryptHashService(HashService):
    - Usa bcrypt.hashpw() para hashear
    - Usa bcrypt.checkpw() para verificar
    - Configurable: rounds (default 12)
    - Salt generado automáticamente
```

**`jwt_token_service.py`** - Implementación con PyJWT

```python
class JWTTokenService(TokenService):
    - Algoritmo: HS256
    - Payload: user_id, email, exp, iat, sub
    - Configurable: secret_key, algorithm, expiration
    - Manejo de tokens expirados/inválidos
```

---

### 🌐 Presentation Layer (`app/presentation/`)

#### Configuration (`config.py`)

**`Settings`** - Configuración con Pydantic

```python
class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    bcrypt_rounds: int = 12
    api_prefix: str = "/api/v1"
    debug: bool = False

    # Lee de .env automáticamente
```

#### API Schemas (`api/schemas/`)

**`auth_schemas.py`** - Esquemas Pydantic para API

```python
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str (8-128 chars)
    username: str (3-50 chars)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    is_verified: bool
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime | None

class ErrorResponse(BaseModel):
    detail: str
```

#### Dependencies (`api/dependencies/`)

**`auth.py`** - Dependency Injection para FastAPI

```python
Funciones:
- get_database_config() -> DatabaseConfig
- get_session() -> AsyncSession
- get_user_repository(session) -> UserRepository
- get_hash_service() -> HashService
- get_token_service() -> TokenService
- get_register_user_use_case(...) -> RegisterUser
- get_login_user_use_case(...) -> LoginUser
- get_current_user(credentials, ...) -> User
```

#### Routes (`api/routes/`)

**`auth.py`** - Endpoints de autenticación

```python
Endpoints:
- POST /auth/register → 201 Created
- POST /auth/login → 200 OK
- GET /auth/me → 200 OK (requiere Bearer token)
```

---

## Modelos de Datos

### User Entity (Dominio)

```python
{
    "id": UUID,
    "email": Email,  # Value Object
    "hashed_password": HashedPassword,  # Value Object
    "username": str,
    "is_active": bool,
    "is_verified": bool,
    "created_at": datetime,
    "updated_at": datetime
}
```

### UserModel (Base de Datos)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

---

## APIs y Endpoints

### POST `/api/v1/auth/register`

**Descripción**: Registra un nuevo usuario

**Request**:

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "username": "john_doe"
}
```

**Response (201)**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "john_doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-11-08T10:30:00Z"
}
```

**Errores**:

- `400 Bad Request`: Email o username duplicado
- `422 Unprocessable Entity`: Validación fallida

---

### POST `/api/v1/auth/login`

**Descripción**: Autenticar usuario y obtener token JWT

**Request**:

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200)**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_at": "2025-11-08T11:00:00Z"
}
```

**Errores**:

- `401 Unauthorized`: Credenciales inválidas o usuario inactivo
- `422 Unprocessable Entity`: Validación fallida

---

### GET `/api/v1/auth/me`

**Descripción**: Obtener información del usuario autenticado

**Headers**:

```
Authorization: Bearer <token>
```

**Response (200)**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "john_doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-11-08T10:30:00Z"
}
```

**Errores**:

- `401 Unauthorized`: Token inválido o expirado
- `403 Forbidden`: Sin token de autorización
- `404 Not Found`: Usuario no existe

---

## Seguridad

### Hashing de Contraseñas

- **Algoritmo**: bcrypt
- **Rounds**: 12 (producción), 4 (tests)
- **Salt**: Generado automáticamente por bcrypt
- **Características**:
  - Resistente a ataques de fuerza bruta
  - Resistente a rainbow tables
  - Adaptive hashing (complejidad configurable)

### JSON Web Tokens (JWT)

**Estructura del Token**:

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "exp": 1699451400, // Timestamp de expiración
  "iat": 1699449600, // Timestamp de creación
  "sub": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Configuración**:

- Algoritmo: HS256 (HMAC SHA-256)
- Expiración: 30 minutos (configurable)
- Secret key: Almacenada en variable de entorno

### Validaciones

**Email**:

- Formato válido según RFC 5322
- Máximo 255 caracteres
- Único en el sistema

**Password**:

- Mínimo 8 caracteres
- Máximo 128 caracteres
- No se almacena en texto plano

**Username**:

- Mínimo 3 caracteres
- Máximo 50 caracteres
- Único en el sistema

---

## Casos de Uso

### 1. Registro de Nuevo Usuario

```python
# Input
register_dto = RegisterUserDTO(
    email="user@example.com",
    password="SecurePass123!",
    username="john_doe"
)

# Proceso
1. Validar formato de datos (Pydantic)
2. Validar email único (Repository)
3. Validar username único (Repository)
4. Crear Email value object
5. Hashear password → HashedPassword
6. Crear User entity
7. Guardar en base de datos
8. Retornar UserResponseDTO

# Output
UserResponseDTO(
    id="550e8400-...",
    email="user@example.com",
    username="john_doe",
    is_active=True,
    is_verified=False,
    created_at=datetime(...)
)
```

### 2. Login de Usuario

```python
# Input
login_dto = LoginDTO(
    email="user@example.com",
    password="SecurePass123!"
)

# Proceso
1. Buscar usuario por email
2. Verificar que usuario existe
3. Verificar contraseña con bcrypt
4. Verificar que usuario está activo
5. Generar JWT token
6. Calcular fecha de expiración
7. Retornar TokenDTO

# Output
TokenDTO(
    access_token="eyJhbGci...",
    token_type="bearer",
    expires_at=datetime(...)
)
```

### 3. Actualización de Usuario

```python
# Ejemplo: Cambiar email
user = await repository.find_by_id(user_id)
new_email = Email("newemail@example.com")
user.update_email(new_email)
await repository.update(user)
```

### 4. Desactivación de Usuario

```python
user = await repository.find_by_id(user_id)
user.deactivate()
await repository.update(user)
# El usuario ya no podrá hacer login
```

---

## Archivos del Proyecto

**Total**: 41 archivos de código + 10 archivos de tests = **183 tests**

---

## Variables de Entorno

```bash
# .env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/argentum
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
BCRYPT_ROUNDS=12
API_PREFIX=/api/v1
DEBUG=True
```

---

## Comandos Útiles

```bash
# Ejecutar API
uv run fastapi dev app/main.py

# Tests
uv run pytest                          # Todos los tests
uv run pytest tests/unit/             # Solo unitarios
uv run pytest tests/e2e/              # Solo E2E
uv run pytest --cov=app               # Con cobertura

# Code Quality
bash scripts/lint.sh                   # Linting + type checking
bash scripts/format.sh                 # Formateo de código
bash scripts/clean.sh                  # Limpiar cache
```

---
