# Re-Search Setup Guide

This guide walks you through setting up the Re-Search application from scratch.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Database Setup](#database-setup)
5. [Environment Variables](#environment-variables)
6. [Running the Application](#running-the-application)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have the following installed:

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.9+ | Backend runtime |
| Node.js | 18+ | Frontend runtime |
| Yarn | 1.22+ | Package manager |
| Neo4j | 5.x | Graph database |

---

## Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Neo4j Configuration
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password-here

# Database Configuration (SQLite for development)
DATABASE_URL=sqlite:///./research.db

# JWT Configuration
JWT_SECRET=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Step 5: Seed Sample Data (Optional)

```bash
python seed_data.py
```

### Step 6: Start the Backend Server

```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

✅ Backend should now be running at `http://localhost:8001`

---

## Frontend Setup

### Step 1: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 2: Install Dependencies

```bash
yarn install
```

### Step 3: Configure Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
# Backend API URL (leave empty if using proxy)
REACT_APP_BACKEND_URL=

# Development settings
DANGEROUSLY_DISABLE_HOST_CHECK=true
HOST=0.0.0.0
```

### Step 4: Start the Frontend Server

```bash
yarn start
```

✅ Frontend should now be running at `http://localhost:3000`

---

## Database Setup

### SQLite (Default - No Setup Required)

SQLite database is created automatically at `backend/research.db` when you first run the backend.

### PostgreSQL (Production)

1. Create a PostgreSQL database:
```sql
CREATE DATABASE research_db;
```

2. Update `DATABASE_URL` in `.env`:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/research_db
```

### Neo4j Cloud Setup

1. Create a free account at [Neo4j Aura](https://neo4j.com/cloud/aura/)
2. Create a new database instance
3. Copy the connection URI and credentials
4. Update `.env`:
```env
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
```

### Loading Neo4j Dump File

If you have a `.dump` file:

1. Using Neo4j Desktop:
   - Open Neo4j Desktop
   - Create a new database
   - Click "..." → "Manage" → "Open Folder"
   - Copy dump file to the folder
   - Run: `neo4j-admin database load --from-path=<dump-file> neo4j`

2. Using Neo4j Aura:
   - Use the Import feature in Aura Console
   - Upload your dump file

---

## Environment Variables

### Backend Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `NEO4J_URI` | Yes | Neo4j connection URI | `neo4j+s://xxx.neo4j.io` |
| `NEO4J_USER` | Yes | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Yes | Neo4j password | `secret123` |
| `DATABASE_URL` | No | SQL database URL | `sqlite:///./research.db` |
| `JWT_SECRET` | Yes | Secret for JWT signing | `my-secret-key` |
| `JWT_ALGORITHM` | No | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token expiry in minutes | `1440` |

### Frontend Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `REACT_APP_BACKEND_URL` | No | Backend API URL | `http://localhost:8001` |
| `DANGEROUSLY_DISABLE_HOST_CHECK` | No | Disable host check | `true` |
| `HOST` | No | Server host | `0.0.0.0` |

---

## Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
yarn start
```

### Using Supervisor (Production)

```bash
sudo supervisorctl restart backend frontend
sudo supervisorctl status
```

### Verify Installation

1. Backend Health Check:
```bash
curl http://localhost:8001/api/health
# Expected: {"status":"healthy","neo4j":"connected","database":"connected"}
```

2. Frontend: Open `http://localhost:3000` in browser

---

## Troubleshooting

### "Invalid Host header" Error
**Solution:** Add to `frontend/.env`:
```env
DANGEROUSLY_DISABLE_HOST_CHECK=true
```

### "Could not validate credentials" Error
**Cause:** JWT token expired or invalid
**Solution:** Clear localStorage and login again

### Neo4j Connection Failed
**Cause:** Invalid credentials or network issue
**Solution:** 
1. Verify credentials in `.env`
2. Check if Neo4j instance is running
3. Backend will fallback to local Neo4j at `bolt://localhost:7687`

### "Module not found" Errors
**Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
yarn install
```

### Database Tables Not Created
**Solution:** Restart the backend - tables are created on startup:
```bash
sudo supervisorctl restart backend
```

---

## Quick Reference

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost:3000 | 3000 |
| Backend API | http://localhost:8001 | 8001 |
| API Docs (Swagger) | http://localhost:8001/docs | 8001 |
| API Docs (ReDoc) | http://localhost:8001/redoc | 8001 |

---

## Next Steps

1. Create a user account at `/register`
2. Complete interest onboarding
3. Search for papers
4. Like papers to get personalized recommendations
5. Check the `/recommendations` page for suggestions
