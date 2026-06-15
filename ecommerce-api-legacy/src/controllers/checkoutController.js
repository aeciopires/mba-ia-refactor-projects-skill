const userModel = require('../models/userModel');
const courseModel = require('../models/courseModel');
const enrollmentModel = require('../models/enrollmentModel');

function simulatePayment(card) {
  return card.startsWith('4') ? 'PAID' : 'DENIED';
}

async function processCheckout({ name, email, password, courseId, card }) {
  if (!name || !email || !courseId || !card) {
    throw Object.assign(new Error('Campos obrigatórios: name, email, courseId, card'), { status: 400 });
  }

  const course = await courseModel.findById(courseId);
  if (!course) {
    throw Object.assign(new Error('Curso não encontrado'), { status: 404 });
  }

  let user = await userModel.findByEmail(email);
  if (!user) {
    const newId = await userModel.create({ name, email, password });
    user = { id: newId };
  }

  const status = simulatePayment(card);
  if (status === 'DENIED') {
    throw Object.assign(new Error('Pagamento recusado'), { status: 400 });
  }

  const enrollmentId = await enrollmentModel.create(user.id, courseId);
  await enrollmentModel.createPayment(enrollmentId, course.price, status);
  await enrollmentModel.logAudit(`Checkout curso ${courseId} por ${user.id}`);

  return { msg: 'Sucesso', enrollment_id: enrollmentId };
}

module.exports = { processCheckout };
