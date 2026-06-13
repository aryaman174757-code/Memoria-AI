# MEMORIA AI

An AI-powered Personal Operating System - your second brain, memory system, productivity platform, and AI assistant.

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- Make (optional)

### Quick Start with Docker Compose

```bash
# Clone the repository
git clone https://github.com/your-org/memoria-ai.git
cd memoria-ai

# Copy environment variables
cp .env.example .env

# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

### Development Setup

#### Backend
```bash
cd apps/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd apps/frontend
npm install
npm run dev
```

## 📁 Project Structure

```
memoria-ai/
├── apps/
│   ├── backend/          # FastAPI backend
│   ├── frontend/         # Next.js frontend
│   ├── mobile/           # React Native mobile
│   └── desktop/          # Electron desktop
├── packages/            # Shared packages
├── docs/                # Documentation
└── deployments/         # Deployment configurations
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11, PostgreSQL, Redis, RabbitMQ
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **AI/ML**: LangChain, OpenAI, Anthropic, ChromaDB
- **DevOps**: Docker, Kubernetes, GitHub Actions

## 📝 Documentation

Full documentation is available in the `docs/` directory.

## 📄 License

MIT License - see LICENSE file for details.
