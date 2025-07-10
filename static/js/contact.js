document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');

    contactForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Reset error messages
        document.querySelectorAll('.error-message').forEach(error => {
            error.textContent = '';
            error.style.display = 'none';
        });

        // Get form values
        const formData = {
            name: document.getElementById('name').value.trim(),
            email: document.getElementById('email').value.trim(),
            message: document.getElementById('message').value.trim()
        };

        try {
            const response = await fetch('/contact', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            const result = await response.json();

            if (result.success) {
                contactForm.reset();
                // Flash message will be handled by Flask redirect
                window.location.reload(); // Reload to show flash message
            } else {
                for (const [field, message] of Object.entries(result.errors)) {
                    const errorElement = document.getElementById(`${field}-error`);
                    errorElement.textContent = message;
                    errorElement.style.display = 'block';
                }
            }
        } catch (error) {
            console.error('Error:', error);
            const messageError = document.getElementById('message-error');
            messageError.textContent = 'An error occurred. Please try again.';
            messageError.style.display = 'block';
        }
    });
});