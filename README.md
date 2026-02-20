📘 Anime Manager API

API RESTful para gerenciamento de animes com autenticação de usuários.

Projeto backend profissional desenvolvido com foco em:

Arquitetura organizada

Segurança com autenticação

Banco relacional

Deploy em produção

Estrutura escalável

🚀 API online (Railway):

🔗 anime-manager-api-production.up.railway.app/docs

🧠 Sobre o Projeto

O Anime Manager API permite:

Cadastro de usuários

Login com geração de token JWT

Cadastro de animes

Listagem de animes

Estrutura preparada para relacionamento usuário ↔ animes

Deploy em ambiente de produção

Projeto desenvolvido aplicando boas práticas de backend moderno.

🏗 Arquitetura do Projeto
app/
 ├── main.py
 ├── models.py
 ├── schemas.py
 ├── database.py
 ├── routers/
 │    ├── auth.py
 │    └── animes.py
 └── ...

Arquitetura em camadas:

Models (SQLAlchemy)

Schemas (Pydantic)

Routers (separação por domínio)

Database connection

Configuração via variáveis de ambiente

🛠 Stack Tecnológica
Backend

Python

FastAPI

SQLAlchemy

Pydantic

JWT Authentication

Banco de Dados

PostgreSQL

DevOps

Docker

Docker Compose

Railway (Deploy)

Versionamento

Git

GitHub

🔐 Segurança

Hash de senha

Autenticação via JWT

Separação de schemas para entrada e saída

Variáveis de ambiente para dados sensíveis

📦 Modelos Principais
👤 User

id

username

email

hashed_password

is_active

🎬 Anime

id

title

genre

episodes

🔄 Fluxo da Aplicação
Client (Web/Mobile)
        ↓
     FastAPI
        ↓
   SQLAlchemy ORM
        ↓
   PostgreSQL (Railway)
▶️ Executar Localmente
1️⃣ Clonar repositório
git clone https://github.com/Erik02T/anime-manager-api.git
cd anime-manager-api
2️⃣ Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
3️⃣ Instalar dependências
pip install -r requirements.txt
4️⃣ Configurar variáveis de ambiente

Criar arquivo .env:

DATABASE_URL=postgresql://user:password@localhost:5432/anime_db
SECRET_KEY=sua_chave_super_secreta
5️⃣ Rodar aplicação
uvicorn app.main:app --reload
🐳 Rodar com Docker
docker-compose -f docker-compose.dev.yml up --build
📡 Endpoints Principais
🔐 Auth

POST /register

POST /login

🎬 Animes

POST /animes

GET /animes

📊 Diferenciais do Projeto

✔ Estrutura organizada
✔ Separação de responsabilidades
✔ Banco relacional real
✔ Deploy em produção
✔ Containerização
✔ Preparado para integração mobile

🎯 Objetivo

Este projeto faz parte da minha jornada como desenvolvedor backend, aplicando conceitos como:

APIs REST

Segurança

Banco relacional

Deploy em cloud

Estrutura profissional de projeto

👨‍💻 Autor

Erik Sant
Backend Developer em formação
Foco em Python, APIs REST e arquitetura escalável

GitHub: https://github.com/Erik02T

📈 Próximas Melhorias

Relacionamento User ↔ Anime

Testes automatizados

CI/CD

Documentação Swagger aprimorada

Sistema de favoritos

Paginação

