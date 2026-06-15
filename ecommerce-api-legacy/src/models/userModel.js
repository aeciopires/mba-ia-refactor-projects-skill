const { run, get } = require('../config/database');
const bcrypt = require('bcrypt');

async function findByEmail(email) {
  return get('SELECT * FROM users WHERE email = ?', [email]);
}

async function findById(id) {
  return get('SELECT id, name, email FROM users WHERE id = ?', [id]);
}

async function create({ name, email, password }) {
  const hash = await bcrypt.hash(password || 'default-password', 10);
  const result = await run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, hash]);
  return result.lastID;
}

async function verifyPassword(plaintext, hash) {
  return bcrypt.compare(plaintext, hash);
}

async function remove(id) {
  return run('DELETE FROM users WHERE id = ?', [id]);
}

module.exports = { findByEmail, findById, create, verifyPassword, remove };
