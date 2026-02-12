# Deployment Instructions

## Frontend Deployment (Vercel)

### Prerequisites
- A Vercel account
- The Vercel CLI installed (`npm i -g vercel`)

### Steps
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Deploy to Vercel:
   ```bash
   vercel --prod
   ```

### Environment Variables Required
- `NEXT_PUBLIC_API_URL`: URL of your deployed backend (e.g., https://your-backend.hf.space)
- `NEXTAUTH_URL`: URL of your deployed frontend (e.g., https://your-frontend.vercel.app)
- `NEXTAUTH_SECRET`: Generate with `openssl rand -base64 32`
- `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret

## Backend Deployment (Hugging Face Spaces)

### Prerequisites
- A Hugging Face account
- Git LFS installed (for larger files)

### Steps
1. Create a new Space on Hugging Face
2. Choose "Docker" as the SDK
3. Add the following files to your repository:
   - All backend files
   - Dockerfile.hf
   - space.yaml

### Environment Variables Required
- `DATABASE_URL`: Database connection string (PostgreSQL recommended)
- `SECRET_KEY`: Secret key for JWT tokens
- `ALGORITHM`: Algorithm for JWT (HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration in minutes
- `FRONTEND_URL`: URL of your deployed frontend
- `OPENAI_API_KEY`: OpenAI API key (if using OpenAI)
- `OPENROUTER_API_KEY`: OpenRouter API key (if using OpenRouter)
- `GROQ_API_KEY`: Groq API key (if using Groq)

## Architecture
- Frontend (Next.js) hosted on Vercel
- Backend (FastAPI) hosted on Hugging Face Spaces
- MCP Server (FastAPI) for AI agent integration
- Database (PostgreSQL recommended)

## Notes
- Ensure CORS settings allow communication between frontend and backend
- The MCP server should be accessible from both the frontend and any AI services
- For production, use HTTPS for all connections