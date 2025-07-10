document.addEventListener('DOMContentLoaded', function() {
    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date').min = today;

    const appointmentForm = document.getElementById('appointment-form');
    const notification = document.getElementById('notification');
    const appointmentsContainer = document.getElementById('appointments-container');

    // Fetch and display appointments
    fetchAppointments();

    // Form submission
    appointmentForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Reset error messages
        document.querySelectorAll('.error-message').forEach(error => error.style.display = 'none');

        // Get form values
        const formData = {
            fullname: document.getElementById('fullname').value.trim(),
            email: document.getElementById('email').value.trim(),
            phone: document.getElementById('phone').value.trim(),
            doctor: document.getElementById('doctor').value,
            date: document.getElementById('date').value,
            time: document.getElementById('time').value,
            reason: document.getElementById('reason').value.trim()
        };

        try {
            const response = await fetch('/appointment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            const result = await response.json();

            if (result.success) {
                appointmentForm.reset();
                notification.textContent = result.message;
                notification.classList.add('show');
                setTimeout(() => notification.classList.remove('show'), 3000);
                fetchAppointments();
            } else {
                for (const [field, message] of Object.entries(result.errors)) {
                    document.getElementById(`${field}-error`).textContent = message;
                    document.getElementById(`${field}-error`).style.display = 'block';
                }
            }
        } catch (error) {
            console.error('Error:', error);
            notification.textContent = 'An error occurred. Please try again.';
            notification.classList.add('show');
            setTimeout(() => notification.classList.remove('show'), 3000);
        }
    });

    // Fetch appointments
    async function fetchAppointments() {
        try {
            const response = await fetch('/appointments');
            const result = await response.json();
            if (result.success) {
                displayAppointments(result.appointments);
            } else {
                console.error('Error:', result.message);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    // Display appointments
    function displayAppointments(appointments) {
        if (appointments.length === 0) {
            appointmentsContainer.innerHTML = "<p>You don't have any upcoming appointments.</p>";
            return;
        }

        appointments.sort((a, b) => new Date(a.date + 'T' + a.time) - new Date(b.date + 'T' + b.time));

        let html = '';
        appointments.forEach(appointment => {
            const appointmentDate = new Date(appointment.date + 'T' + appointment.time);
            const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            const formattedDate = appointmentDate.toLocaleDateString('en-US', dateOptions);
            const timeOptions = { hour: '2-digit', minute: '2-digit' };
            const formattedTime = appointmentDate.toLocaleTimeString('en-US', timeOptions);

            html += `
                <div class="appointment-card" data-id="${appointment.id}">
                    <h3>${appointment.doctor}</h3>
                    <p class="appointment-info">Date: ${formattedDate}</p>
                    <p class="appointment-info">Time: ${formattedTime}</p>
                    <p class="appointment-info">Reason: ${appointment.reason}</p>
                    <div class="appointment-actions">
                        <button class="appointment-btn reschedule-btn" onclick="rescheduleAppointment(${appointment.id})">Reschedule</button>
                        <button class="appointment-btn cancel-btn" onclick="cancelAppointment(${appointment.id})">Cancel</button>
                    </div>
                </div>
            `;
        });

        appointmentsContainer.innerHTML = html;
    }

    // Reschedule appointment
    window.rescheduleAppointment = async function(id) {
        try {
            const response = await fetch(`/appointment/reschedule/${id}`, { method: 'POST' });
            const result = await response.json();
            if (result.success) {
                const appointment = (await (await fetch('/appointments')).json()).appointments.find(app => app.id === id);
                if (appointment) {
                    document.getElementById('fullname').value = appointment.fullname;
                    document.getElementById('email').value = appointment.email;
                    document.getElementById('phone').value = appointment.phone;
                    document.getElementById('doctor').value = appointment.doctor;
                    document.getElementById('reason').value = appointment.reason;
                    fetchAppointments();
                    document.querySelector('.appointment-form').scrollIntoView({ behavior: 'smooth' });
                }
            } else {
                console.error('Error:', result.message);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    };

    // Cancel appointment
    window.cancelAppointment = async function(id) {
        if (confirm('Are you sure you want to cancel this appointment?')) {
            try {
                const response = await fetch(`/appointment/cancel/${id}`, { method: 'POST' });
                const result = await response.json();
                if (result.success) {
                    notification.textContent = result.message;
                    notification.classList.add('show');
                    setTimeout(() => notification.classList.remove('show'), 3000);
                    fetchAppointments();
                } else {
                    console.error('Error:', result.message);
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }
    };
});