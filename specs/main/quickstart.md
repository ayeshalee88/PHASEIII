# Quickstart Guide: Phase II – Full-Stack Todo Web Application

## Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (or Neon account)
- Git

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database connection details
python -m src.main  # to initialize the database
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your backend API URL
npm run dev
```

### 4. Environment Variables

#### Backend (.env)
```
DATABASE_URL=postgresql://username:password@localhost:5432/todoapp
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Frontend (.env)
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Running the Application

### Backend
```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
```

## API Testing
The API will be available at `http://localhost:8000/api/docs` for interactive documentation.

## Database Initialization
The application will automatically create tables on first run if they don't exist.