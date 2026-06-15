const sqlite3 = require('sqlite3').verbose();
const settings = require('./settings');

const db = new sqlite3.Database(settings.dbPath);

function run(sql, params = []) {
  return new Promise((resolve, reject) =>
    db.run(sql, params, function (err) {
      if (err) reject(err);
      else resolve({ lastID: this.lastID, changes: this.changes });
    })
  );
}

function get(sql, params = []) {
  return new Promise((resolve, reject) =>
    db.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)))
  );
}

function all(sql, params = []) {
  return new Promise((resolve, reject) =>
    db.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)))
  );
}

async function initDb() {
  await run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, pass TEXT)`);
  await run(`CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER DEFAULT 1)`);
  await run(`CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(course_id) REFERENCES courses(id))`);
  await run(`CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT,
    FOREIGN KEY(enrollment_id) REFERENCES enrollments(id))`);
  await run(`CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)`);

  const existingUser = await get('SELECT id FROM users LIMIT 1');
  if (!existingUser) {
    const bcrypt = require('bcrypt');
    const hash = await bcrypt.hash('senha123', 10);
    await run("INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
      ['Leonan', 'leonan@fullcycle.com.br', hash]);
    await run("INSERT INTO courses (title, price, active) VALUES (?, ?, ?)", ['Clean Architecture', 997.00, 1]);
    await run("INSERT INTO courses (title, price, active) VALUES (?, ?, ?)", ['Docker', 497.00, 1]);
    await run("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", [1, 1]);
    await run("INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)", [1, 997.00, 'PAID']);
  }
}

module.exports = { db, run, get, all, initDb };
