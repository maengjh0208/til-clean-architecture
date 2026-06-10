# til-clean-architecture

FastAPI + Clean Architecture 학습 프로젝트입니다.

## 기술 스택

| 분류 | 기술 |
|------|------|
| Framework | FastAPI 0.136.1 |
| Runtime | Python 3.12 |
| DB | MySQL 8.0 |
| ORM | SQLAlchemy 2.0 |
| Migration | Alembic |
| DI Container | dependency-injector |
| Auth | JWT (python-jose) |
| Password | passlib + bcrypt |
| ID | ULID (py-ulid) |
| Settings | pydantic-settings |
| Infra | Docker / Docker Compose |

## 아키텍처

클린 아키텍처의 핵심은 **의존성 방향**입니다. 외부(인프라, 인터페이스)가 내부(도메인, 애플리케이션)에 의존하며, 내부는 외부를 모릅니다.

```
Interface (Controller)
    ↓
Application (Service / Use Case)
    ↓
Domain (Entity + Repository Interface)
    ↑
Infrastructure (Repository 구현체 + DB 모델)
```

### 각 레이어 역할

| 레이어 | 위치 | 역할 |
|--------|------|------|
| Domain | `*/domain/` | 순수 도메인 모델(dataclass), 리포지토리 인터페이스 |
| Application | `*/application/` | 비즈니스 유스케이스 (Service) |
| Infrastructure | `*/infra/` | SQLAlchemy 모델, 리포지토리 구현체 |
| Interface | `*/interface/` | FastAPI 라우터, 요청/응답 스키마 |

## 프로젝트 구조

```
.
├── main.py                  # FastAPI 앱 진입점
├── containers.py            # IoC 컨테이너 (dependency-injector)
├── database.py              # SQLAlchemy 엔진 / 세션
├── middleware.py            # HTTP 미들웨어 (유저 컨텍스트 추출, 로깅)
├── config.py                # 환경 변수 설정 (pydantic-settings)
├── context_vars.py          # ContextVar (요청 스코프 유저 정보)
├── common/
│   ├── auth.py              # JWT 발급/검증, 인증 의존성
│   └── logger.py            # 로거 설정
├── user/                    # User 도메인
│   ├── domain/
│   │   ├── user.py          # User 엔티티
│   │   └── repository/
│   │       └── user_repo.py # IUserRepository 인터페이스
│   ├── application/
│   │   └── user_service.py  # 회원가입, 로그인, CRUD 유스케이스
│   ├── infra/
│   │   ├── db_models/       # SQLAlchemy 테이블 모델
│   │   └── repository/      # IUserRepository 구현체
│   └── interface/
│       └── controllers/
│           └── user_controller.py  # /users 라우터
├── note/                    # Note 도메인
│   ├── domain/
│   │   ├── note.py          # Note, Tag 엔티티
│   │   └── repository/
│   │       └── note_repo.py # INoteRepository 인터페이스
│   ├── application/
│   │   └── note_service.py  # 노트 CRUD 유스케이스
│   ├── infra/
│   │   ├── db_models/       # SQLAlchemy 테이블 모델
│   │   └── repository/      # INoteRepository 구현체
│   └── interface/
│       └── controllers/
│           └── note_controller.py  # /notes 라우터
├── example/                 # 학습 예제
│   ├── ch10_01/             # BackgroundTask
│   └── ch11_01/             # ContextVar + Middleware
├── migrations/              # Alembic 마이그레이션
├── utils/
│   ├── crypto.py            # bcrypt 암호화
│   └── db_utils.py          # DB 유틸리티
├── Dockerfile
└── docker-compose.yml
```

## API 엔드포인트

### User

| Method | Endpoint | 설명 | 인증 |
|--------|----------|------|------|
| POST | `/users/` | 회원 가입 | - |
| GET | `/users/` | 이메일로 회원 조회 | - |
| GET | `/users/list` | 회원 목록 조회 (페이징) | Admin |
| PUT | `/users/` | 회원 정보 수정 | User |
| DELETE | `/users/{user_id}` | 회원 탈퇴 | - |
| POST | `/users/login` | 로그인 (JWT 발급) | - |

### Note

| Method | Endpoint | 설명 | 인증 |
|--------|----------|------|------|
| POST | `/notes/` | 노트 생성 | User |
| GET | `/notes/` | 노트 목록 조회 (페이징) | User |
| GET | `/notes/{note_id}` | 노트 단건 조회 | User |
| PUT | `/notes/{note_id}` | 노트 수정 | User |
| DELETE | `/notes/{note_id}` | 노트 삭제 | User |
| GET | `/notes/tags` | 태그로 노트 조회 | User |

## 실행 방법

### 1. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 값을 채웁니다.

```env
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=til_db
MYSQL_USER=til_user
MYSQL_PASSWORD=til_password
SECRET_KEY=your-secret-key
ALGORITHM=HS256
```

### 2. Docker Compose로 실행

```bash
docker compose up --build
```

앱이 `http://localhost:8000` 에서 시작됩니다.  
DB가 healthy 상태가 될 때까지 앱 컨테이너는 대기합니다.

### 3. DB 마이그레이션

컨테이너 기동 후 마이그레이션을 실행합니다.

```bash
docker compose exec app alembic upgrade head
```

### 4. API 문서 확인

| URL | 설명 |
|-----|------|
| `http://localhost:8000/docs` | Swagger UI |
| `http://localhost:8000/redoc` | ReDoc |

### 로컬 개발 (venv)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

> 로컬 실행 시 `database.py`의 DB 호스트(`db`)를 `localhost`로 변경하거나 환경 변수로 분리해야 합니다.

## 주요 설계 포인트

- **IoC 컨테이너** — `containers.py`에서 `dependency-injector`로 Service/Repository 의존성을 선언하고 FastAPI DI(`Depends`)와 연결합니다.
- **Repository 패턴** — 도메인 레이어는 인터페이스(`IUserRepository`, `INoteRepository`)만 알고, 구체 구현은 인프라 레이어에 위치합니다.
- **ULID** — UUID 대신 정렬 가능한 ULID를 PK로 사용합니다.
- **JWT 인증** — 로그인 시 `HS256` 서명 토큰 발급, 미들웨어에서 요청마다 토큰을 파싱해 `ContextVar`에 유저 정보를 저장합니다.
- **Alembic** — 스키마 변경은 마이그레이션 파일로 관리합니다.
