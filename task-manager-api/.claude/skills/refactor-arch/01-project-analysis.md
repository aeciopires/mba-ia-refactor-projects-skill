# Project Analysis — Detection Heuristics

## 1. Language Detection

### Python
- Files: `*.py`, `requirements.txt`, `Pipfile`, `pyproject.toml`
- Count `.py` files, identify main entry point (`app.py`, `main.py`, `run.py`, `wsgi.py`)

### JavaScript / Node.js
- Files: `package.json`, `*.js`, `*.ts`
- Check `package.json` for `"main"` field and `"scripts"."start"`

### Java
- Files: `pom.xml`, `build.gradle`, `*.java`
- Look for `src/main/java/` structure

### Go
- Files: `go.mod`, `*.go`

---

## 2. Framework Detection

### Python Frameworks
| Framework | Signals |
|-----------|---------|
| Flask | `from flask import Flask`, `app = Flask(__name__)`, `@app.route`, `flask` in requirements.txt |
| FastAPI | `from fastapi import FastAPI`, `uvicorn` in requirements |
| Django | `manage.py`, `settings.py`, `INSTALLED_APPS`, `django` in requirements |
| SQLAlchemy | `from sqlalchemy`, `db.Model`, `flask-sqlalchemy` in requirements |

### Node.js Frameworks
| Framework | Signals |
|-----------|---------|
| Express | `require('express')`, `app.get/post/put/delete`, `app.use()`, `express` in package.json |
| Fastify | `require('fastify')`, `fastify` in package.json |
| NestJS | `@Module`, `@Controller`, `@nestjs/core` in package.json |
| Koa | `require('koa')`, `koa` in package.json |

---

## 3. Database Detection

| DB | Python signals | Node.js signals |
|----|---------------|-----------------|
| SQLite | `import sqlite3`, `sqlite3.connect`, `sqlite:///` URI, `flask-sqlalchemy` + SQLite URI | `require('sqlite3')`, `new sqlite3.Database()` |
| PostgreSQL | `psycopg2`, `postgresql://` URI | `pg`, `knex` with postgres |
| MySQL | `mysql-connector-python`, `mysql://` URI | `mysql2`, `mysql` |
| MongoDB | `pymongo`, `mongoengine` | `mongoose`, `mongodb` |

---

## 4. Architecture Classification

Examine directory structure and file count to classify current architecture:

### Monolithic — Everything in 1–4 files
- Signals: `app.py` + `models.py` + `controllers.py` all in root, or single `app.js`/`AppManager.js`
- Note: God Class or God File pattern likely present

### Partially Organized — Some structure but incomplete
- Signals: `models/` and `routes/` exist but no `controllers/`; or business logic still inside route files
- Note: Missing layers will be MVC gaps to fill

### MVC — Full separation of concerns
- Signals: `models/`, `views/` or `routes/`, `controllers/`, `config/`, `middlewares/` all present and each file has a single responsibility

---

## 5. Domain Detection

Identify the business domain by scanning:
- Table names in SQL `CREATE TABLE` statements or ORM model class names
- Route prefixes (e.g., `/produtos`, `/orders`, `/tasks`, `/courses`)
- Field names in models (e.g., `preco`, `estoque` → e-commerce; `due_date`, `priority` → task manager; `enrollment`, `course` → LMS)

---

## 6. Source File Inventory

For each source file collect:
- Path relative to project root
- Line count
- Primary responsibility (inferred from filename and imports)
- Dominant pattern (routes, models, business logic, utility, config)

---

## 7. Summary Output Format

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <Python | JavaScript | ...>
Framework:     <Flask 3.x | Express 4.x | ...>
Dependencies:  <comma-separated key packages>
Domain:        <short description, e.g., "E-commerce API — produtos, pedidos, usuários">
Architecture:  <Monolithic | Partially Organized | MVC>  — brief description
Source files:  <N> files analyzed
DB tables:     <comma-separated table or model names>
================================
```
