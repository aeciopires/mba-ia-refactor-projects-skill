# Architecture Guidelines — MVC Target Pattern

## Target Directory Structure

### Python / Flask
```
src/
├── config/
│   └── settings.py          ← all config read from os.environ; no literals
├── models/
│   ├── __init__.py
│   └── <entity>_model.py    ← one file per domain entity
├── controllers/
│   ├── __init__.py
│   └── <entity>_controller.py
├── views/                   ← (or routes/)
│   ├── __init__.py
│   └── <entity>_routes.py
├── middlewares/
│   └── error_handler.py
└── app.py                   ← composition root only
```

### Node.js / Express
```
src/
├── config/
│   └── settings.js
├── models/
│   └── <entity>Model.js
├── controllers/
│   └── <entity>Controller.js
├── routes/
│   └── <entity>Routes.js
├── middlewares/
│   └── errorHandler.js
└── app.js
```

---

## Layer Responsibilities

### config/
- Read ALL environment variables here; never `os.environ.get()` inside models or controllers.
- Provide a single config object imported by other layers.
- Example (Python):
  ```python
  import os
  SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')
  DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
  DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
  ```
- Example (Node.js):
  ```js
  module.exports = {
    port: process.env.PORT || 3000,
    dbPath: process.env.DB_PATH || ':memory:',
    paymentKey: process.env.PAYMENT_KEY,
  };
  ```

### models/
- **Allowed:** Database access (queries, ORM calls), data validation at persistence level, serialization helpers.
- **Forbidden:** `request` / `response` objects, business rules (e.g., discount calculation), sending notifications.
- Use parameterized queries exclusively — no string concatenation.
- `to_dict()` / `to_public_dict()` must NOT include password, secret_key, or token fields.
- One model file per domain entity (`produto_model.py`, `userModel.js`).

### controllers/
- **Allowed:** Orchestrate model calls, apply business rules, decide which HTTP status code to return.
- **Forbidden:** Direct SQL queries, `request.get_json()` / `req.body` access, `jsonify()` / `res.json()` calls.
- Receive plain Python/JS values (not request objects); return plain dicts/objects (not response objects).
- Example signature (Python): `def criar_pedido(usuario_id: int, itens: list) -> dict`
- Example signature (Node.js): `async function processCheckout({ userId, courseId, card }) { ... }`

### views / routes/
- **Allowed:** Parse request (extract body/params/query), call the appropriate controller function, serialize and return the HTTP response.
- **Forbidden:** Business logic, database queries, calculations.
- Maximum ~5 lines per route handler body.
- Example (Python):
  ```python
  @bp.route('/pedidos', methods=['POST'])
  def criar_pedido_route():
      dados = request.get_json()
      resultado = pedido_controller.criar_pedido(dados['usuario_id'], dados['itens'])
      return jsonify(resultado), 201
  ```
- Example (Node.js):
  ```js
  router.post('/checkout', async (req, res, next) => {
    try {
      const result = await checkoutController.process(req.body);
      res.json(result);
    } catch (err) { next(err); }
  });
  ```

### middlewares/
- Centralized error handler is **mandatory**:
  - Python (Flask): `@app.errorhandler(Exception)` that catches unhandled exceptions and returns JSON `{"error": "..."}`.
  - Node.js (Express): `app.use((err, req, res, next) => { res.status(500).json({ error: err.message }); })`.
- Authentication middleware for admin routes (verify API key from `Authorization` header or `config.adminKey`).

### app.py / app.js (composition root)
- Import and register blueprints/routers.
- Initialize database.
- Register middleware.
- **No business logic, no route definitions, no SQL.**

---

## Invariants to Enforce

| Rule | Python check | Node.js check |
|------|-------------|---------------|
| No SQL in routes | grep `cursor.execute` in `views/` | grep `db.run\|db.get\|db.all` in `routes/` |
| No `request` in models | grep `from flask import.*request` in `models/` | grep `req\.body\|req\.params` in `models/` |
| No plaintext secrets | grep `SECRET_KEY\s*=\s*["']` in any `.py` file | grep `paymentKey.*:.*["']pk_live` in `.js` |
| No `print()`/`console.log()` in handlers | grep `print(` in `controllers/` or `views/` | grep `console\.log` in `controllers/` or `routes/` |
| Passwords use bcrypt | grep `hashlib.md5\|base64` in `models/` | grep `badCrypto\|btoa\|base64` in `models/` |

---

## Entry Point Validation (Phase 3)

After refactoring, run the application and verify:

1. **Boot check:** `python src/app.py` or `node src/app.js` starts without errors.
2. **Health endpoint:** `GET /health` returns HTTP 200.
3. **Core endpoints:** Each original route must respond with the same HTTP status code it did before refactoring.
4. **No anti-patterns remaining:** Re-run the detection signals from `02-antipatterns-catalog.md` against the new code.
