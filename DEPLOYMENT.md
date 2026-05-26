# NEXUS V3 — Deployment & Operations Guide

## 🚀 Environments

| Environment | Platform | URL |
| :--- | :--- | :--- |
| **Development** | Local Machine | `http://localhost:3000` |
| **Staging** | Vercel / Docker | `https://nexus-staging.vercel.app` |
| **Production** | Vercel / AWS-ECS | `https://nexus.ai` |

## 📦 Cloud Setup Steps

### 1. Database (Supabase / Neon)
1. Create a new PostgreSQL instance.
2. Copy the **Transaction Pooler** connection string.
3. Update `DATABASE_URL` in production secrets.

### 2. Authentication (Clerk)
1. Configure a new Application in Clerk Dashboard.
2. Add authorized Redirect URLs (Vercel domain).
3. Copy `CLERK_PUBLISHABLE_KEY` and `CLERK_SECRET_KEY`.

### 3. Backend Deployment (Docker/VPS)
The backend is Docker-ready. 
```bash
docker build -t nexus-backend ./apps/backend
docker run -p 8000:8000 --env-file .env nexus-backend
```

### 4. Frontend Deployment (Vercel)
Vercel will automatically detect the Next.js project. Ensure the following environment variables are set in Vercel UI:
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `CLERK_SECRET_KEY`
- `NEXT_PUBLIC_API_URL` (Pointer to your Backend URL)

## 🛠 CI/CD Pipeline
- **Backend CI**: Runs unit tests on every push to `main`.
- **Frontend CI**: Validates the Next.js build and TypeScript types.
