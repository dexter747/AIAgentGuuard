# AgentGuard

**AI Agent Testing & Monitoring Platform** - Production-ready system with real-time analytics

---

## ✅ Current Status

**Backend**: ✅ Running on http://localhost:8000  
**Frontend**: ✅ Running on http://localhost:3000  
**Database**: ✅ PostgreSQL seeded with 50 sample traces  
**API**: ✅ 5 analytics endpoints operational

### Demo Credentials
- **Email**: demo@democorp.com  
- **API Key**: `ag_live_demo_key_1234567890abcdef`  
- **Organization**: Demo Corp (PRO plan)

---

## 🎯 What's Built

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and pnpm 8+
- Python 3.11+
- PostgreSQL 14+
- Redis 7+

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd AgentGaurd

# Install frontend dependencies
pnpm install

# Install backend dependencies
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Setup Environment Variables

```bash
# Frontend
cp apps/web/.env.example apps/web/.env.local
cp apps/admin/.env.example apps/admin/.env.local

# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your database credentials
```

### Database Setup

```bash
# Create PostgreSQL database
createdb agentguard

# Run migrations
cd backend
alembic upgrade head
```

### Start Development Servers

```bash
# Terminal 1: Start all frontend apps
pnpm dev

# Terminal 2: Start backend
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

**Access:**
- Web App: http://localhost:3000
- Admin Portal: http://localhost:3001
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📁 Project Structure

```
AgentGaurd/
├── apps/
│   ├── web/                # User-facing dashboard (Next.js)
│   └── admin/              # Admin portal (Next.js)
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Config, database
│   │   ├── models/        # SQLAlchemy models
│   │   └── services/      # Business logic
│   ├── alembic/           # Database migrations
│   └── main.py            # FastAPI entry point
├── packages/               # Shared packages (future)
├── docs/                   # Documentation
└── pnpm-workspace.yaml    # Monorepo config
```

---

## 🛠 Development

### Frontend Development

```bash
# Run specific app
pnpm dev:web    # User dashboard
pnpm dev:admin  # Admin portal

# Build for production
pnpm build

# Lint
pnpm lint
```

### Backend Development

```bash
cd backend

# Run with auto-reload
uvicorn main:app --reload

# Run tests
pytest

# Format code
black .

# Type checking
mypy .

# Create new migration
alembic revision -m "description"

# Apply migrations
alembic upgrade head
```

---

## 📚 Documentation

- [How It Works](docs/HowItWorks.md) - Non-technical explanation
- [Integration Flow](docs/Integration-Flow.md) - Technical deep-dive
- [Tech Stack](docs/TechStack.md) - Architecture & deployment
- [Business Model](docs/Business-Model.md) - Pricing & API keys
- [SRS](docs/SRS.md) - Software requirements
- [Architecture](docs/Architecture.md) - System architecture

---

## 🔑 API Key Setup

1. Sign up at http://localhost:3000
2. Get your API key from dashboard
3. Use in your agent:

```python
import agentguard

agentguard.init(api_key="ag_live_your_key_here")
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests (when implemented)
pnpm test
```

---

## 🚢 Deployment

See [TechStack.md](docs/TechStack.md) for deployment options:
- Vercel (frontend)
- Railway/Render (backend)
- Managed PostgreSQL
- Managed Redis

---

## 📝 License

Proprietary - All rights reserved

---

## 🤝 Contributing

This is a private project. Contact the team for contribution guidelines.

---

## 📧 Support

- Email: support@agentguard.io
- Docs: docs.agentguard.io
- Issues: GitHub Issues
