function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('error-message');
    const successMessage = document.getElementById('success-message');

    errorMessage.style.display = 'none';
    successMessage.style.display = 'none';

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la solicitud');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                successMessage.textContent = `¡Login exitoso!`;
                successMessage.style.display = 'block';
                window.location.href = '/home';
            } else {
                errorMessage.textContent = data.error || 'Credenciales inválidas';
                errorMessage.style.display = 'block';
            }
        })
        .catch(error => {
            errorMessage.textContent = 'Error al conectar con el servidor';
            errorMessage.style.display = 'block';
        });
}