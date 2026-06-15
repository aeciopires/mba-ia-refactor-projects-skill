const { get, all } = require('../config/database');

async function findById(id) {
  return get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
}

async function findAll() {
  return all('SELECT * FROM courses');
}

module.exports = { findById, findAll };
