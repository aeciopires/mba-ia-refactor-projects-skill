const enrollmentModel = require('../models/enrollmentModel');

async function financialReport() {
  const rows = await enrollmentModel.findAllWithDetails();
  const courseMap = {};
  for (const row of rows) {
    if (!courseMap[row.course]) {
      courseMap[row.course] = { course: row.course, revenue: 0, students: [] };
    }
    if (row.student) {
      const paid = row.status === 'PAID' ? row.amount : 0;
      courseMap[row.course].revenue += paid;
      courseMap[row.course].students.push({ student: row.student, paid: row.amount || 0 });
    }
  }
  return Object.values(courseMap);
}

module.exports = { financialReport };
