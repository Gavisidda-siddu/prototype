function showForm(type) {
  console.log(`showForm called with type: ${type}`);
  if (type !== 'login' && type !== 'register') {
    type = 'login'; // Default to login if type is invalid
    console.log('Invalid type, defaulting to login');
  }
  document.querySelectorAll('.tab').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.form').forEach(form => form.classList.remove('active'));

  if (type === 'login') {
    document.querySelector('.tab:nth-child(1)').classList.add('active');
    document.getElementById('login-form').classList.add('active');
    console.log('Login form displayed');
  } else {
    document.querySelector('.tab:nth-child(2)').classList.add('active');
    document.getElementById('register-form').classList.add('active');
    console.log('Register form displayed');
  }
}