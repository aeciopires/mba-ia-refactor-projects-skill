const { run, get, all } = require('../config/database');

async function create(userId, courseId) {
  const result = await run(
    'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
    [userId, courseId]
  );
  return result.lastID;
}

async function createPayment(enrollmentId, amount, status) {
  const result = await run(
    'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
    [enrollmentId, amount, status]
  );
  return result.lastID;
}

async function logAudit(action) {
  return run(
    "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
    [action]
  );
}

async function findAllWithDetails() {
  return all(`
    SELECT c.title AS course, u.name AS student, p.amount, p.status
    FROM courses c
    LEFT JOIN enrollments e ON e.course_id = c.id
    LEFT JOIN users u ON u.id = e.user_id
    LEFT JOIN payments p ON p.enrollment_id = e.id
  `);
}

async function removeByUserId(userId) {
  return run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
}

async function removePaymentsByUserId(userId) {
  return run(`
    DELETE FROM payments WHERE enrollment_id IN (
      SELECT id FROM enrollments WHERE user_id = ?
    )`, [userId]);
}

module.exports = {
  create, createPayment, logAudit, findAllWithDetails,
  removeByUserId, removePaymentsByUserId,
};
