# SAHAY Deployment Guide

This guide outlines the complete process for deploying the SAHAY platform in a production-like prototype environment using **Vercel**, **Render**, and **Supabase**.

## Architecture Overview

```text
www.sahay-domain.com
        ↓
     Vercel (Next.js Frontend)
        ↓
     Render (FastAPI Backend)
        ↓
    Supabase (PostgreSQL)
```

## Step 1: Prepare the Database (Supabase)
1. Go to [Supabase](https://supabase.com) and create a new project.
2. Navigate to **Project Settings -> Database**.
3. Obtain the **Connection String (URI)**. Ensure you use the IPv4 compatible pooler string if your backend host (like Render) requires IPv4.
4. Replace `[YOUR-PASSWORD]` with the actual database password.

## Step 2: Deploy the Backend (Render)
1. Go to [Render](https://render.com) and create a new **Web Service**.
2. Connect your GitHub repository containing the SAHAY code.
3. Configure the following settings:
   - **Root Directory:** `backend`
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add the following **Environment Variables**:
   - `DATABASE_URL`: The Supabase connection string from Step 1.
   - `JWT_SECRET_KEY`: A secure random string.
   - `AI_PROVIDER`: `gemini` or `openai` (or `mock`).
   - `GEMINI_API_KEY`: Your real LLM API Key.
   - `FRONTEND_URL`: (You will update this later after Vercel deployment, e.g., `https://sahay.vercel.app`).
5. Click **Deploy**.
6. Verify deployment by visiting `https://[YOUR-RENDER-URL]/health`. It should return `{"application": "healthy", ...}`.

## Step 3: Run Database Migrations
To securely structure the production database, you need to run Alembic migrations.
1. Connect to the Render web console (Shell) for your deployed backend.
2. Run `alembic upgrade head`.
3. (Optional) If you want demo data in production, run `python seed.py`. Be extremely careful not to seed fake data in a real live environment.

## Step 4: Deploy the Frontend (Vercel)
1. Go to [Vercel](https://vercel.com) and create a new project.
2. Import your GitHub repository.
3. Set the **Root Directory** to `frontend`.
4. Add the following **Environment Variables**:
   - `NEXT_PUBLIC_API_URL`: `https://[YOUR-RENDER-URL]/api`
5. Click **Deploy**.

## Step 5: Secure the Pipeline
1. **Update CORS:** Go back to your Render dashboard and set the `FRONTEND_URL` variable to your new Vercel domain. This ensures the backend strictly accepts requests only from your frontend.
2. **Verify Secrets:** Ensure absolutely no API keys (OpenAI, Gemini, Supabase) are added to Vercel's environment variables. They must remain isolated on Render.

## Step 6: Final End-to-End Test
- Visit your Vercel URL.
- Test the registration flow.
- Login with the admin credentials.
- Approve the registration request.
- Test the victim check-in and verify the AI analysis successfully returns a dynamic distress score.
