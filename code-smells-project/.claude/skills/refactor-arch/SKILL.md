# Skill: refactor-arch
# Architectural Audit & Refactoring to MVC

You are an expert software architect executing a 3-phase audit and refactoring process.
Work methodically through each phase in order. Never skip a phase or merge them.

## Reference Files (read all before starting)
- `01-project-analysis.md` — heuristics for detecting language, framework, DB, architecture
- `02-antipatterns-catalog.md` — 14 anti-patterns with detection signals and severity
- `03-audit-report-template.md` — exact format for the Phase 2 report
- `04-architecture-guidelines.md` — MVC target structure and layer invariants
- `05-refactoring-playbook.md` — 10 concrete before/after transformation patterns

---

## PHASE 1 — PROJECT ANALYSIS

**Goal:** Understand the project without modifying any file.

Steps:
1. Read all reference files listed above so you have full context.
2. List all source files (exclude `node_modules/`, `__pycache__/`, `.git/`, `venv/`).
3. Read each source file completely.
4. Apply the detection heuristics from `01-project-analysis.md` to determine:
   - Language and version (check requirements.txt or package.json)
   - Framework and version
   - Key dependencies
   - Application domain (infer from table names, route prefixes, model class names)
   - Current architecture classification (Monolithic / Partially Organized / MVC)
   - Number of source files and approximate total lines of code
   - Database tables or ORM models
5. Print the Phase 1 summary block exactly as shown in `01-project-analysis.md`.

**Do NOT modify any file during Phase 1.**

---

## PHASE 2 — ARCHITECTURE AUDIT

**Goal:** Find all anti-pattern instances, produce a structured report, then WAIT for user confirmation.

Steps:
1. For each anti-pattern in `02-antipatterns-catalog.md`, scan every source file for its detection signals.
2. Record every instance found: exact file path (relative to project root), exact line numbers, and a 1-line code quote.
3. Classify severity using the catalog (CRITICAL / HIGH / MEDIUM / LOW).
4. Generate the audit report using the template from `03-audit-report-template.md`:
   - Order findings: CRITICAL → HIGH → MEDIUM → LOW
   - Each finding must have File, Description (with code quote), Impact, Recommendation
   - Minimum 5 findings; at least 1 must be CRITICAL or HIGH
   - Deprecated API usage must always be reported when found
5. Print the complete report.
6. **STOP. Print exactly:** `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`
7. **Wait for the user to type `y` before continuing. If they type `n`, stop.**

**Do NOT modify any file during Phase 2.**

---

## PHASE 3 — REFACTORING

**Goal:** Restructure the project to MVC, eliminate all CRITICAL and HIGH findings.

**Only execute after the user confirms with `y`.**

Steps:

### 3.1 — Create target structure
Following `04-architecture-guidelines.md`, create these directories under the project root:
```
src/config/
src/models/
src/controllers/
src/views/   (Python) or src/routes/  (Node.js)
src/middlewares/
```

### 3.2 — Apply transformations
Apply the relevant transformations from `05-refactoring-playbook.md` for every finding:

| Finding category | Transformation to apply |
|-----------------|------------------------|
| SQL Injection | T-01 Parameterized Queries |
| Hardcoded Credentials | T-02 Extract Secrets to Env Vars |
| God Class / God File | T-03 Decompose God Class |
| Business Logic in Routes | T-04 Extract Controller from Route |
| Weak Password Storage | T-05 Password Hashing with bcrypt |
| N+1 Query | T-06 Eliminate N+1 with JOIN |
| Bare Except | T-07 Centralized Error Handler |
| Mutable Global State | T-08 Remove Mutable Global State |
| Unauthenticated Admin | T-09 Authentication Middleware |
| Magic Numbers | T-10 Named Constants |
| Deprecated API | Replace with current API per framework docs |
| Sensitive Data in Response | Remove sensitive fields from to_dict() / serialization |

### 3.3 — Migration rules
- **Python/Flask:**
  - Move `SECRET_KEY`, `DEBUG`, and DB path to `src/config/settings.py` reading from `os.environ`
  - Create `src/models/<entity>_model.py` with parameterized queries only
  - Create `src/controllers/<entity>_controller.py` — no `request`/`response` objects
  - Create `src/views/<entity>_routes.py` with Blueprint, route handlers ≤ 5 lines each
  - Create `src/middlewares/error_handler.py` with `register_error_handlers(app)`
  - `src/app.py` registers blueprints, error handlers, calls `db.init_app(app)` — no logic

- **Node.js/Express:**
  - Move all config to `src/config/settings.js` reading from `process.env`
  - Create `src/models/<entity>Model.js` — Promise-based wrappers around DB calls with parameterized queries
  - Create `src/controllers/<entity>Controller.js` — async functions, no req/res
  - Create `src/routes/<entity>Routes.js` — Router with try/catch delegating to controller
  - Create `src/middlewares/errorHandler.js` — `(err, req, res, next)` handler
  - `src/app.js` wires everything together

### 3.4 — Validate the result
After writing all files:

1. **Boot check** — Start the application:
   - Python: `python src/app.py` (or `flask run` if configured)
   - Node.js: `node src/app.js` (or `npm start` if available)
   - Report any startup errors and fix them before continuing.

2. **Endpoint check** — Test each original route with curl or equivalent:
   - For each route that existed before, verify it returns the same HTTP status code.
   - Report the results as a checklist.

3. **Anti-pattern re-scan** — Confirm CRITICAL and HIGH findings are eliminated.

### 3.5 — Print completion summary
```
================================
PHASE 3: REFACTORING COMPLETE
================================
New Project Structure:
src/
├── config/settings.py (or settings.js)
├── models/
│   └── ...
├── controllers/
│   └── ...
├── views/ (or routes/)
│   └── ...
├── middlewares/error_handler.py (or errorHandler.js)
└── app.py (or app.js)

Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero CRITICAL/HIGH anti-patterns remaining
================================
```

---

## Important Rules

- **Never** modify files during Phase 1 or Phase 2.
- **Always** pause and print the `[y/n]` prompt at the end of Phase 2.
- **Never** proceed to Phase 3 without an explicit `y` from the user.
- If the project already has partial MVC structure (e.g., has `models/` but no `controllers/`), build on top of the existing structure rather than recreating it.
- If a file is part of an existing well-structured layer (e.g., SQLAlchemy model classes with relationships), keep it and improve it (fix deprecated API, remove password exposure) rather than replacing it entirely.
- Generate only what is needed — do not add features beyond the refactoring scope.
