# Anti-Patterns Catalog

Each entry includes: name, severity, detection signals (language-specific), impact, and recommended fix.

---

## CRITICAL

### AP-01 — SQL Injection
**Severity:** CRITICAL  
**Detection signals:**
- Python: `"SELECT " + var`, `f"WHERE id = {id}"`, `"INSERT INTO ... VALUES ('" + nome + "'"`, `cursor.execute("... WHERE id = " + str(id))`
- Node.js: Template literals in SQL strings, `"SELECT * FROM users WHERE id = " + id`  

**Impact:** An attacker can read, modify, or delete any data in the database; bypass authentication.  
**Fix:** Always use parameterized queries: `cursor.execute("SELECT * FROM t WHERE id = ?", [id])` (Python) or `db.get("SELECT * FROM t WHERE id = ?", [id], ...)` (Node.js).

---

### AP-02 — Hardcoded Credentials / Secrets
**Severity:** CRITICAL  
**Detection signals:**
- `SECRET_KEY = "..."` or `SECRET_KEY = 'some-literal-string'` in source files
- `password = "prod_password_123"`, `api_key = "pk_live_..."`, `dbPass: "secret"` in config or utility files
- Any `.js` or `.py` file with literals that look like keys, tokens or passwords  

**Impact:** Credentials committed to version control are permanently exposed; attackers with repo access can exploit production systems.  
**Fix:** Move all secrets to environment variables (`os.environ.get('SECRET_KEY')` / `process.env.SECRET_KEY`) and load them from a `.env` file (not committed) or a secrets manager.

---

### AP-03 — God Class / God File
**Severity:** CRITICAL  
**Detection signals:**
- Single class or file with >3 of: DB initialization, route definitions, business logic, authentication, payment processing, email/notification
- Python: `models.py` > 200 lines mixing DB queries, business rules, and serialization for multiple domains
- Node.js: Class with methods `initDb()`, `setupRoutes()`, and payment logic all together  

**Impact:** Impossible to test in isolation; any change risks breaking unrelated features; zero cohesion.  
**Fix:** Extract each responsibility into its own module/class following Single Responsibility Principle.

---

### AP-04 — Unauthenticated Admin / Privileged Endpoint
**Severity:** CRITICAL  
**Detection signals:**
- Route path contains `/admin/`, `/internal/`, `/debug/` with no authentication middleware applied
- Route executes destructive operations (DELETE all rows, execute raw SQL) without identity verification  

**Impact:** Any unauthenticated client can destroy or exfiltrate data.  
**Fix:** Add an authentication middleware to all admin routes; require at minimum an API key from environment or JWT verification.

---

## HIGH

### AP-05 — Weak / Reversible Password Storage
**Severity:** HIGH  
**Detection signals:**
- Python: `hashlib.md5(pwd.encode()).hexdigest()`, direct plaintext comparison `senha == input`
- Node.js: `Buffer.from(pwd).toString('base64')`, any base64 or MD5 used as password hash  

**Impact:** If the database is compromised, all user passwords can be recovered in minutes.  
**Fix:** Use bcrypt (`bcrypt.hashpw` / `bcrypt.compare`) or Argon2. Never store or compare passwords in plaintext or reversible encoding.

---

### AP-06 — Business Logic Inside Route / View Handlers
**Severity:** HIGH  
**Detection signals:**
- Route function body contains SQL queries, discount calculations, stock updates, email sending logic
- Python: `@app.route` function longer than ~20 lines with business rules
- Node.js: `app.get/post` callback with nested DB calls and business conditionals  

**Impact:** Logic is untestable in isolation; routes become giant functions; violates MVC.  
**Fix:** Extract business logic to Controller functions; route handler should only parse request, call controller, return response.

---

### AP-07 — Mutable Global State
**Severity:** HIGH  
**Detection signals:**
- Module-level mutable variables used across request handlers: `globalCache = {}`, `totalRevenue = 0`, `db_connection = None` modified by functions
- Python: module-level `db_connection` reassigned inside a function  

**Impact:** State bleeds between requests under concurrent load; race conditions; hard to test.  
**Fix:** Use dependency injection or request-scoped context (`flask.g`, Express middleware locals) instead of mutable module globals.

---

### AP-08 — Sensitive Data Exposure in API Response
**Severity:** HIGH  
**Detection signals:**
- `to_dict()` method or serialization includes `password`, `senha`, `secret_key`, `token` fields
- `/health` or `/info` endpoint returns internal config values or credentials  

**Impact:** Passwords and secrets are transmitted to API clients; stored in logs.  
**Fix:** Explicitly exclude sensitive fields from serialization; create a `to_public_dict()` method that omits security fields.

---

## MEDIUM

### AP-09 — N+1 Query Problem
**Severity:** MEDIUM  
**Detection signals:**
- SQL query inside a Python `for` loop: `for row in rows: cursor.execute("SELECT ... WHERE id = " + str(row["id"]))`
- Node.js: `forEach` with a `db.get()` callback inside another `db.all()` callback
- SQLAlchemy: accessing a relationship attribute on each object in a list without eager loading  

**Impact:** For N items, generates N+1 database roundtrips; performance degrades linearly.  
**Fix:** Use JOINs, `IN` clauses, or SQLAlchemy eager loading (`joinedload`) to fetch related data in a single query.

---

### AP-10 — Missing Input Validation
**Severity:** MEDIUM  
**Detection signals:**
- Route handler passes raw `request.get_json()` values directly to model/DB functions without type, length, or format checks
- No validation on numeric fields (negative price, invalid priority range)
- Email fields accepted without format validation  

**Impact:** Malformed data corrupts the database; unexpected types cause runtime errors.  
**Fix:** Validate all user-supplied inputs at the controller layer before passing to models.

---

### AP-11 — Bare Except / Silent Error Swallowing
**Severity:** MEDIUM  
**Detection signals:**
- Python: `except:` with no exception type, or `except Exception: pass`
- Node.js: `catch(err) {}` with empty body or only `console.log`  

**Impact:** Catches `KeyboardInterrupt`, `SystemExit`, and other non-recoverable signals; hides bugs.  
**Fix:** Always catch specific exception types; log the exception with context; return appropriate HTTP error responses.

---

### AP-12 — Deprecated API Usage
**Severity:** MEDIUM  
**Detection signals:**
- Python/SQLAlchemy 2.0+: `Model.query.get(id)` → deprecated, use `db.session.get(Model, id)`
- Python/SQLAlchemy: `SQLALCHEMY_TRACK_MODIFICATIONS` config key → deprecated/removed
- Node.js/Express: `require('body-parser')` as separate package → built in as `express.json()` since Express 4.16
- Node.js: `req.param()` → removed in Express 5  

**Impact:** Code will break on framework upgrades; deprecation warnings pollute logs.  
**Fix:** Use the current API as documented in the framework's migration guide.

---

## LOW

### AP-13 — Magic Numbers / Unlabeled Constants
**Severity:** LOW  
**Detection signals:**
- Numeric literals in business logic without named constants: `if faturamento > 10000`, `* 0.1`, `if priority < 1 or priority > 5`
- Threshold values repeated in multiple places  

**Impact:** Reader cannot understand the business meaning of the number; changing it requires finding every occurrence.  
**Fix:** Extract to named constants: `DISCOUNT_THRESHOLD_HIGH = 10_000`, `DISCOUNT_RATE_HIGH = 0.10`.

---

### AP-14 — print() / console.log() as Logging
**Severity:** LOW  
**Detection signals:**
- `print(...)` inside route or model functions in Python
- `console.log(...)` inside route handlers in Node.js
- No `import logging` / `const logger = require('winston')` present  

**Impact:** No log levels, no timestamps, no structured output; cannot filter by severity; not compatible with log aggregation systems.  
**Fix:** Use `logging` module (Python) with `logging.info()` / `logging.error()`, or a structured logger like `winston` (Node.js).
