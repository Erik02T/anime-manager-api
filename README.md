📘 Anime Manager API

API RESTful para gerenciamento de animes com autenticação de usuários.

Projeto backend profissional desenvolvido com foco em:

Arquitetura organizada

Segurança com autenticação

Banco relacional

Deploy em produção

Estrutura escalável

🚀 API Online (Produção)

🔗 Swagger (Railway):
https://anime-manager-api-production.up.railway.app/docs

🧠 Sobre o Projeto

O Anime Manager API permite:

Cadastro de usuários

Login com geração de token JWT

Cadastro de animes

Listagem de animes

Exclusão de animes

Deploy em ambiente de produção (Railway)

Banco PostgreSQL em nuvem

Projeto desenvolvido aplicando boas práticas modernas de backend.

📸 Demonstração do Projeto
🔥 1️⃣ API rodando em produção (Railway)

✔ Aplicação iniciando
✔ Uvicorn rodando
✔ Deploy ativo
✔ Logs funcionando

🗄 2️⃣ Banco PostgreSQL em produção (Railway)

✔ Tabela animes criada
✔ Dados persistidos em nuvem
✔ Integração API ↔ Banco funcionando

📡 3️⃣ Endpoint funcionando via Swagger

✔ Requisição autenticada
✔ Token JWT via Authorization
✔ Retorno 200 OK
✔ Dados vindos do PostgreSQL

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

Routers (Separação por domínio)

Database Connection

Configuração via variáveis de ambiente

🛠 Stack Tecnológica
🔹 Backend

Python

FastAPI

SQLAlchemy

Pydantic

JWT Authentication

🔹 Banco de Dados

PostgreSQL (Railway)

🔹 DevOps

Docker

Docker Compose

Railway (Deploy)

🔹 Versionamento

Git

GitHub

🔐 Segurança

Hash de senha

Autenticação JWT

Proteção de rotas com Bearer Token

Variáveis de ambiente (.env)

Separação de schemas (input/output)

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
 PostgreSQL (Railway Cloud)
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
4️⃣ Criar arquivo .env
DATABASE_URL=postgresql://user:password@localhost:5432/anime_db
SECRET_KEY=sua_chave_super_secreta
AUTO_CREATE_TABLES=true
5️⃣ Rodar aplicação
uvicorn app.main:app --reload
🐳 Rodar com Docker
docker-compose -f docker-compose.dev.yml up --build
📡 Endpoints Principais
🔐 Auth

POST /auth/register

POST /auth/login

🎬 Animes

POST /animes/

GET /animes/

DELETE /animes/{anime_id}

📊 Diferenciais do Projeto

✔ API em produção real
✔ Banco PostgreSQL em nuvem
✔ Autenticação JWT
✔ Estrutura profissional
✔ Containerização com Docker
✔ Deploy automatizado
✔ Logs monitorados
✔ Preparado para integração mobile

🎯 Objetivo

Este projeto demonstra minha capacidade de:

Criar APIs REST completas

Estruturar backend profissional

Trabalhar com banco relacional real

Implementar autenticação segura

Fazer deploy em cloud

Utilizar Docker em ambiente real

👨‍💻 Autor

Erik Sant
Backend Developer
Foco em Python, APIs REST e arquitetura escalável

GitHub:
https://github.com/Erik02T

📈 Próximas Melhorias

Relacionamento User ↔ Anime

Testes automatizados (Pytest)

CI/CD Pipeline

Paginação

Sistema de favoritos

Rate limiting

Logs estruturados

Monitoramento![WhatsApp Image 2026-02-21 at 1 38 29 PM](https://github.com/user-attachments/assets/601eba3b-54cb-49ec-81e6-651126087b30)
![WhatsApp Image 2026-02-21 at 1 37 12 PM](https://github.com/user-attachments/assets/be3b51bf-a0ea-4598-8b1b-d8fea1a7d400)
![WhatsApp Image 2026-02-21 at 1 32 47 PM](https://github.com/user-attachments/assets/740727c2-5ff5-4952-b291-f114255e6568)
