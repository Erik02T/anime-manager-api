# 🎌 Anime Manager API

A professional RESTful API for managing Anime & Manga collections.

Built with modern backend architecture using FastAPI, PostgreSQL, Docker and JWT authentication.

---

## 🧠 Project Overview

Anime Manager API is a full-featured backend system that allows users to:

- Register and authenticate securely (JWT)
- Create, update, delete and list animes
- Store persistent data using PostgreSQL
- Run inside Docker containers
- Be deployed to cloud environments

This project was built following real-world backend architecture principles.

---

## 🏗️ Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn

### Database
- PostgreSQL (Production)
- SQLite (Development)

### Authentication
- JWT (PyJWT)
- Passlib (bcrypt hashing)

### Testing
- Pytest
- FastAPI TestClient
- httpx

### DevOps
- Docker
- Docker Compose
- Railway (Cloud Deployment)

---

## 📂 Project Structure


anime-manager/
│
├── app/
│ ├── main.py
│ ├── database.py
│ ├── models.py
│ ├── schemas.py
│ ├── crud.py
│ ├── routers/
│ └── core/
│
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md


---

## 🔐 Authentication Flow

1. User registers
2. Password is hashed with bcrypt
3. User logs in
4. JWT access token is generated
5. Protected routes require Bearer Token

---

## 🐳 Running Locally with Docker

```bash
docker compose up --build

Access:

http://localhost:8000/docs
💻 Running Locally without Docker
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
🧪 Running Tests
pytest
☁️ Deployment

Deployed using Render with:

Managed PostgreSQL database

Environment variables configuration

Production-ready ASGI server

📈 Future Improvements

Role-based permissions (Admin/User)

Refresh tokens

Pagination & filtering

CI/CD pipeline

Mobile client integration

👨‍💻 Author

Erik Sant
Backend Developer
Brazil 🇧🇷

📜 License

This project is for educational and portfolio purposes.


