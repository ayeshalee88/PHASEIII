# Deployment Guide: FastAPI Backend + MCP Server to Hugging Face Spaces

## Prerequisites

- A Hugging Face account
- Git installed on your system
- Git LFS installed (for larger files)

## Step-by-Step Deployment Instructions

### 1. Create a New Hugging Face Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Fill in the details:
   - **Space Name**: `backendphaseiii`
   - **SDK**: Docker
   - **Hardware**: CPU (or GPU if needed)
   - **Visibility**: Public or Private (as per your preference)
4. Click "Create Space"

### 2. Clone Your Space Repository

1. Once the Space is created, click on the "Files" tab
2. Click the "Clone or download" button
3. Copy the Git URL
4. Clone the repository locally:
   ```bash
   git clone https://huggingface.co/spaces/ayishaalee/backendphaseiii
   cd backendphaseiii
   ```

### 3. Prepare Your Files

Copy the following files to your Space repository:

1. **Dockerfile** - From this project (Dockerfile.hf)
2. **Requirements file** - From this project (huggingface_requirements.txt)
3. **Backend directory** - Entire `backend/` folder
4. **MCP Server directory** - Entire `mcp_server/` folder
5. **README.md** - From this project (README.md.hf)

### 4. Organize Your Project Structure

Your Space repository should have this structure:
```
backendphaseiii/
├── Dockerfile
├── requirements.txt
├── backend/
│   ├── main.py
│   ├── src/
│   ├── api/
│   ├── models/
│   ├── database/
│   ├── requirements.txt
│   └── ...
├── mcp_server/
│   ├── server.py
│   ├── requirements.txt
│   └── ...
└── README.md
```

### 5. Set Up Environment Variables (Secrets)

1. Go to your Space page on Hugging Face
2. Click on the "Files" tab
3. Click on "Settings" in the left sidebar
4. Go to "Secrets" section
5. Add the following secrets:

#### Required Secrets:
- `DATABASE_URL`: Your database connection string (e.g., PostgreSQL or SQLite)
- `SECRET_KEY`: A long, random secret key for JWT tokens
- `FRONTEND_URL`: The URL of your deployed frontend (e.g., https://your-app.vercel.app)

#### Optional Secrets (for AI features):
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `GROQ_API_KEY`: Your Groq API key

### 6. Commit and Push Your Changes

```bash
git add .
git commit -m "Add FastAPI backend and MCP server"
git push origin main
```

### 7. Monitor the Build Process

1. Go to your Space page
2. Click on the "Logs" tab
3. Monitor the build process - it may take several minutes
4. Look for any error messages if the build fails

### 8. Test Your Deployment

1. Once the build is complete, your Space will be available at:
   `https://ayishaalee-backendphaseiii.hf.space`
2. Test the API endpoints:
   - `GET /` - Should return "Todo API is running!"
   - `GET /health` - Should return health check information

### 9. Update Your Frontend Configuration

Update your Vercel frontend to use the new backend URL:
- Set `NEXT_PUBLIC_API_URL` to `https://ayishaalee-backendphaseiii.hf.space`

## Troubleshooting

### Common Issues:

1. **Build fails due to memory limits**:
   - Reduce the number of dependencies
   - Use multi-stage builds to reduce image size

2. **Application crashes after startup**:
   - Check the logs for error messages
   - Ensure all required environment variables are set

3. **Database connection issues**:
   - Verify your DATABASE_URL is correct
   - Ensure your database allows connections from Hugging Face servers

4. **Port binding issues**:
   - Make sure the application binds to 0.0.0.0:7860
   - Hugging Face requires the application to run on port 7860

### Useful Commands:

- Check logs: Go to your Space page → Logs tab
- Restart Space: Settings → Restart Space
- Check environment: Add a test endpoint that returns environment variables

## Maintenance

- Monitor your Space regularly for any issues
- Update dependencies periodically
- Scale resources if needed based on usage
- Backup your data if using persistent storage

## Scaling Considerations

- For increased traffic, consider upgrading to a more powerful hardware tier
- Use a managed database service for production applications
- Implement caching if needed for performance