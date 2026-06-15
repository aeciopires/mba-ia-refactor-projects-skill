# Refactoring Playbook

Each transformation targets one or more anti-patterns from `02-antipatterns-catalog.md`.
All examples show the minimal before/after; adapt field names and table names to the project.

---

## T-01 — Parameterized Queries (fixes AP-01 SQL Injection)

**Before (Python — string concatenation):**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute(
    "INSERT INTO produtos (nome, preco) VALUES ('" + nome + "', " + str(preco) + ")"
)
```

**After (Python — parameterized):**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute(
    "INSERT INTO produtos (nome, preco) VALUES (?, ?)",
    (nome, preco)
)
```

**Before (Node.js — string concatenation):**
```js
db.get("SELECT * FROM users WHERE email = '" + email + "'", callback);
```

**After (Node.js — parameterized):**
```js
db.get("SELECT * FROM users WHERE email = ?", [email], callback);
```

---

## T-02 — Extract Secrets to Environment Variables (fixes AP-02 Hardcoded Credentials)

**Before (Python):**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
```

**After (Python):**
```python
# src/config/settings.py
import os
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# src/app.py
from config.settings import SECRET_KEY, DEBUG
app.config["SECRET_KEY"] = SECRET_KEY
app.config["DEBUG"] = DEBUG
```

**Before (Node.js):**
```js
const config = {
    dbPass: "senha_super_secreta_prod_123",
    paymentGatewayKey: "pk_live_1234567890abcdef",
};
```

**After (Node.js):**
```js
// src/config/settings.js
module.exports = {
    dbPass: process.env.DB_PASS,
    paymentGatewayKey: process.env.PAYMENT_KEY,
    port: process.env.PORT || 3000,
};
```

---

## T-03 — Decompose God Class (fixes AP-03 God Class)

**Before (Node.js — AppManager handles everything):**
```js
class AppManager {
    constructor() { this.db = new sqlite3.Database(':memory:'); }
    initDb() { /* 20 lines of CREATE TABLE + INSERT */ }
    setupRoutes(app) { /* 100 lines of route + business logic */ }
}
```

**After (split into single-responsibility modules):**
```js
// src/config/database.js
const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database(process.env.DB_PATH || ':memory:');
module.exports = db;

// src/models/userModel.js
const db = require('../config/database');
function findByEmail(email) {
    return new Promise((resolve, reject) =>
        db.get("SELECT * FROM users WHERE email = ?", [email], (err, row) =>
            err ? reject(err) : resolve(row)));
}
module.exports = { findByEmail };

// src/controllers/checkoutController.js
const userModel = require('../models/userModel');
async function process(payload) { /* business logic only */ }
module.exports = { process };

// src/routes/api.js
const router = require('express').Router();
const checkoutController = require('../controllers/checkoutController');
router.post('/checkout', async (req, res, next) => {
    try { res.json(await checkoutController.process(req.body)); }
    catch (err) { next(err); }
});
module.exports = router;
```

---

## T-04 — Extract Controller from Route (fixes AP-06 Business Logic in Routes)

**Before (Python — business logic inside route):**
```python
@app.route('/pedidos', methods=['POST'])
def criar_pedido():
    dados = request.get_json()
    total = 0
    for item in dados['itens']:
        cursor.execute("SELECT preco FROM produtos WHERE id = ?", (item['produto_id'],))
        produto = cursor.fetchone()
        total += produto['preco'] * item['quantidade']
    cursor.execute("INSERT INTO pedidos (usuario_id, total) VALUES (?, ?)", (dados['usuario_id'], total))
    return jsonify({"pedido_id": cursor.lastrowid}), 201
```

**After (Python — route delegates to controller):**
```python
# src/controllers/pedido_controller.py
from models import pedido_model

def criar_pedido(usuario_id: int, itens: list) -> dict:
    return pedido_model.criar(usuario_id, itens)

# src/views/pedido_routes.py
from controllers import pedido_controller

@bp.route('/pedidos', methods=['POST'])
def criar_pedido_route():
    dados = request.get_json()
    resultado = pedido_controller.criar_pedido(dados['usuario_id'], dados['itens'])
    return jsonify(resultado), 201
```

---

## T-05 — Password Hashing with bcrypt (fixes AP-05 Weak Password Storage)

**Before (Python — MD5):**
```python
import hashlib
def set_password(self, pwd):
    self.password = hashlib.md5(pwd.encode()).hexdigest()

def check_password(self, pwd):
    return self.password == hashlib.md5(pwd.encode()).hexdigest()
```

**After (Python — bcrypt):**
```python
import bcrypt
def set_password(self, pwd):
    self.password = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_password(self, pwd):
    return bcrypt.checkpw(pwd.encode(), self.password.encode())
```

**Before (Node.js — badCrypto / base64):**
```js
function badCrypto(pwd) {
    return Buffer.from(pwd).toString('base64').substring(0, 10);
}
```

**After (Node.js — bcrypt):**
```js
const bcrypt = require('bcrypt');
async function hashPassword(pwd) { return bcrypt.hash(pwd, 10); }
async function verifyPassword(pwd, hash) { return bcrypt.compare(pwd, hash); }
```

---

## T-06 — Eliminate N+1 Queries with JOIN (fixes AP-09 N+1 Query)

**Before (Python — query inside loop):**
```python
cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))
pedidos = cursor.fetchall()
for pedido in pedidos:
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?", (pedido["id"],))
    itens = cursor2.fetchall()
    for item in itens:
        cursor3.execute("SELECT nome FROM produtos WHERE id = ?", (item["produto_id"],))
```

**After (Python — single JOIN query):**
```python
cursor.execute("""
    SELECT p.id, p.status, p.total,
           ip.quantidade, ip.preco_unitario,
           pr.nome AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = ip.produto_id
    WHERE p.usuario_id = ?
""", (usuario_id,))
```

---

## T-07 — Centralized Error Handler (fixes AP-11 Bare Except)

**Before (Python — bare except everywhere):**
```python
try:
    result = do_something()
except:
    return jsonify({"error": "Erro interno"}), 500
```

**After (Python — register once in app.py):**
```python
# src/middlewares/error_handler.py
import logging
logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Recurso não encontrado"}), 404

    @app.errorhandler(Exception)
    def unhandled(e):
        logger.exception("Unhandled error")
        return jsonify({"error": "Erro interno do servidor"}), 500

# src/app.py
from middlewares.error_handler import register_error_handlers
register_error_handlers(app)
```

**Before (Node.js — empty catch):**
```js
app.post('/checkout', (req, res) => {
    try { /* ... */ } catch (err) { res.status(500).send("Error"); }
});
```

**After (Node.js — centralized):**
```js
// src/middlewares/errorHandler.js
module.exports = (err, req, res, next) => {
    console.error(err.stack);
    res.status(err.status || 500).json({ error: err.message || 'Internal Server Error' });
};

// src/app.js
const errorHandler = require('./middlewares/errorHandler');
app.use(errorHandler);
```

---

## T-08 — Remove Mutable Global State (fixes AP-07)

**Before (Node.js):**
```js
let globalCache = {};
let totalRevenue = 0;

function logAndCache(key, data) {
    globalCache[key] = data;
}
```

**After (Node.js — request-scoped Map or in-memory store with clear ownership):**
```js
// src/services/cacheService.js
const store = new Map();
function set(key, value) { store.set(key, value); }
function get(key) { return store.get(key); }
module.exports = { set, get };
```

**Before (Python — module-level mutable):**
```python
db_connection = None

def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(...)
    return db_connection
```

**After (Python — Flask application context):**
```python
from flask import g
import sqlite3
from config.settings import DATABASE_PATH

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

---

## T-09 — Authentication Middleware for Admin Routes (fixes AP-04)

**Before (Python — no auth):**
```python
@app.route('/admin/reset-db', methods=['POST'])
def reset_database():
    # deletes all data, no auth check
```

**After (Python — decorator-based auth):**
```python
# src/middlewares/auth.py
from functools import wraps
from flask import request, jsonify
from config.settings import ADMIN_KEY

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get('X-Admin-Key')
        if key != ADMIN_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# src/views/admin_routes.py
@bp.route('/admin/reset-db', methods=['POST'])
@require_admin
def reset_database():
    ...
```

**Before (Node.js — unprotected admin endpoint):**
```js
app.get('/api/admin/financial-report', (req, res) => { /* no auth */ });
```

**After (Node.js — middleware):**
```js
// src/middlewares/auth.js
module.exports = (req, res, next) => {
    const key = req.headers['x-admin-key'];
    if (key !== process.env.ADMIN_KEY) return res.status(401).json({ error: 'Unauthorized' });
    next();
};

// src/routes/api.js
const auth = require('../middlewares/auth');
router.get('/admin/financial-report', auth, reportController.financial);
```

---

## T-10 — Replace Magic Numbers with Named Constants (fixes AP-13)

**Before (Python):**
```python
if faturamento > 10000:
    desconto = faturamento * 0.1
elif faturamento > 5000:
    desconto = faturamento * 0.05
elif faturamento > 1000:
    desconto = faturamento * 0.02
```

**After (Python):**
```python
# src/config/settings.py
DISCOUNT_THRESHOLD_HIGH = 10_000
DISCOUNT_THRESHOLD_MID  = 5_000
DISCOUNT_THRESHOLD_LOW  = 1_000
DISCOUNT_RATE_HIGH = 0.10
DISCOUNT_RATE_MID  = 0.05
DISCOUNT_RATE_LOW  = 0.02

# src/controllers/relatorio_controller.py
from config.settings import (
    DISCOUNT_THRESHOLD_HIGH, DISCOUNT_RATE_HIGH,
    DISCOUNT_THRESHOLD_MID,  DISCOUNT_RATE_MID,
    DISCOUNT_THRESHOLD_LOW,  DISCOUNT_RATE_LOW,
)

def calcular_desconto(faturamento: float) -> float:
    if faturamento > DISCOUNT_THRESHOLD_HIGH:
        return faturamento * DISCOUNT_RATE_HIGH
    if faturamento > DISCOUNT_THRESHOLD_MID:
        return faturamento * DISCOUNT_RATE_MID
    if faturamento > DISCOUNT_THRESHOLD_LOW:
        return faturamento * DISCOUNT_RATE_LOW
    return 0.0
```
