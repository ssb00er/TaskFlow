# ⚡ TaskFlow — Team Task Manager

A full-stack web application for team collaboration with role-based access control, project management, and real-time task tracking.

![TaskFlow Screenshot](https://via.placeholder.com/800x400?text=TaskFlow+Team+Task+Manager)

## 🚀 Live Demo

> **Live URL:** `https://taskflow-production-2b7d.up.railway.app/`

---

## ✨ Features

### Authentication
- JWT-based signup and login
- Role selection: **Admin** or **Member**
- Secure password hashing with bcrypt
- Persistent sessions via localStorage

### Project Management
- Create and manage multiple projects
- Invite team members by email
- Per-project role assignment (Admin/Member)
- Project status tracking: Active → Completed → Archived
- Owner-based access control

### Task System
- Full CRUD for tasks
- Assign tasks to team members
- Status flow: `Todo → In Progress → Review → Done`
- Priority levels: Low / Medium / High / Urgent
- Due dates with overdue detection
- Kanban board view per project

### Dashboard
- Overview stats: total tasks, in-progress, overdue, my tasks
- Recent activity feed
- Overdue task alerts
- Active project summary

### Role-Based Access Control
| Action | Admin | Project Admin | Member |
|--------|-------|--------------|--------|
| Create project | ✅ | ✅ | ✅ |
| Delete any project | ✅ | ❌ | ❌ |
| Add members | ✅ | ✅ | ❌ |
| Remove members | ✅ | ✅ | ❌ |
| Create tasks | ✅ | ✅ | ✅ |
| Edit any task | ✅ | ✅ | ❌ |
| Edit own tasks | ✅ | ✅ | ✅ |
| Update task status | ✅ | ✅ | ✅ |
| Delete own tasks | ✅ | ✅ | ✅ |
| View all users | ✅ | ✅ | ✅ |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python / Flask |
| Database | SQLite (dev) / PostgreSQL (prod) |
| ORM | Flask-SQLAlchemy |
| Auth | Flask-JWT-Extended + Flask-Bcrypt |
| Frontend | Vanilla JS SPA (served by Flask) |
| Deployment | Railway |

---

## 📡 REST API Reference

### Auth
```
POST /api/auth/signup   — Create account
POST /api/auth/login    — Login, get JWT token
GET  /api/auth/me       — Get current user (🔒)
```

### Projects
```
GET    /api/projects              — List accessible projects (🔒)
POST   /api/projects              — Create project (🔒)
GET    /api/projects/:id          — Get project detail (🔒)
PUT    /api/projects/:id          — Update project (🔒 Admin)
DELETE /api/projects/:id          — Delete project (🔒 Owner/Admin)
POST   /api/projects/:id/members  — Add member by email (🔒 Project Admin)
DELETE /api/projects/:id/members/:uid — Remove member (🔒 Project Admin)
```

### Tasks
```
GET    /api/tasks                 — List tasks (🔒, filterable)
POST   /api/tasks                 — Create task (🔒)
GET    /api/tasks/:id             — Get task (🔒)
PUT    /api/tasks/:id             — Update task (🔒)
DELETE /api/tasks/:id             — Delete task (🔒)
```

**Task filters:** `?status=todo|in_progress|review|done`, `?priority=low|medium|high|urgent`, `?project_id=1`

### Dashboard
```
GET /api/dashboard    — Stats, recent & overdue tasks (🔒)
```

### Users
```
GET /api/users        — List all users (🔒)
```

---

## 🗄️ Database Schema

```
Users ──< ProjectMembers >── Projects
                                │
                             Tasks (assignee → Users, creator → Users)
```

- **User**: id, name, email, password_hash, role, created_at
- **Project**: id, name, description, owner_id, status, created_at
- **ProjectMember**: id, project_id, user_id, role, joined_at
- **Task**: id, title, description, project_id, assignee_id, creator_id, status, priority, due_date, created_at, updated_at

---

## 🚂 Deploy to Railway (Step-by-Step)

### 1. Prerequisites
- [Railway account](https://railway.app) (free)
- [GitHub account](https://github.com)
- Git installed locally

### 2. Push to GitHub
```bash
cd taskflow
git init
git add .
git commit -m "Initial commit: TaskFlow app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/taskflow.git
git push -u origin main
```

### 3. Deploy on Railway
1. Go to [railway.app](https://railway.app) → **New Project**
2. Select **Deploy from GitHub repo**
3. Choose your `taskflow` repository
4. Set the **Root Directory** to `backend`
5. Railway auto-detects Python and installs from `requirements.txt`

### 4. Set Environment Variables
In Railway dashboard → your service → **Variables**:

```
SECRET_KEY=your-super-secret-key-change-this-abc123
JWT_SECRET_KEY=your-jwt-secret-change-this-xyz789
```

**Optional (for PostgreSQL):**
```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```
To add PostgreSQL: Railway dashboard → **New** → **Database** → **Add PostgreSQL** → copy the `DATABASE_URL`.

### 5. Generate Domain
Railway dashboard → your service → **Settings** → **Networking** → **Generate Domain**

Your app is now live! 🎉

---

## 💻 Local Development

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/taskflow.git
cd taskflow/backend

# Install dependencies
pip install -r requirements.txt

# Set environment (optional, defaults work for dev)
export SECRET_KEY=dev-secret
export JWT_SECRET_KEY=dev-jwt-secret

# Run the server
python app.py
```

Open [http://localhost:5000](http://localhost:5000)

---

## 🧪 Quick API Test

```bash
# Signup
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@test.com","password":"pass123","role":"admin"}'

# Login (save the token)
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@test.com","password":"pass123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Create a project
curl -X POST http://localhost:5000/api/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Project","description":"First project"}'

# Create a task
curl -X POST http://localhost:5000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Fix the bug","project_id":1,"priority":"high"}'
```

---

## 📁 Project Structure

```
taskflow/
├── backend/
│   ├── app.py              # Flask app factory, blueprints
│   ├── config.py           # Configuration (env vars)
│   ├── database.py         # SQLAlchemy models
│   ├── requirements.txt    # Python dependencies
│   ├── Procfile            # Gunicorn start command
│   ├── railway.toml        # Railway deployment config
│   ├── routes/
│   │   ├── auth.py         # /api/auth/* endpoints
│   │   ├── projects.py     # /api/projects/* endpoints
│   │   ├── tasks.py        # /api/tasks/* endpoints
│   │   ├── users.py        # /api/users/* endpoints
│   │   └── dashboard.py    # /api/dashboard endpoint
│   └── templates/
│       └── index.html      # Full SPA frontend
└── README.md
```

---

## 🔒 Security Features

- Passwords hashed with bcrypt (12 rounds)
- JWT tokens expire after 24 hours
- All API routes require valid JWT except signup/login
- Role checks on every sensitive operation
- Project membership verified on all task operations
- Input validation on all endpoints

---

## 📝 Submission Checklist

- [x] Authentication (Signup/Login with JWT)
- [x] Project management (CRUD + member management)
- [x] Task creation, assignment & status tracking
- [x] Dashboard with stats and overdue alerts
- [x] REST APIs with proper HTTP status codes
- [x] SQLite database with relational schema
- [x] Role-based access control (Admin/Member)
- [x] Input validation on all endpoints
- [x] Railway deployment configuration
- [x] README with deployment instructions

---

*Built with ⚡ Flask + Vanilla JS*
