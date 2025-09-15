document.addEventListener('DOMContentLoaded', () => {
    // Get all the necessary form and container elements
    const signupBox = document.getElementById('signup-box');
    const otpBox = document.getElementById('otp-box');
    const successBox = document.getElementById('success-box'); // Get the new success box

    const signupForm = document.getElementById('signup-form');
    const otpForm = document.getElementById('otp-form');

    // Get the specific error and success message divs
    const emailErrorDiv = document.getElementById('email-error');
    const otpErrorDiv = document.getElementById('otp-error');
    const successMessageDiv = document.getElementById('success-message'); // Get the message div inside success-box

    // Hide all dynamic messages by default when the page loads
    emailErrorDiv.style.display = 'none';
    otpErrorDiv.style.display = 'none';
    successBox.style.display = 'none'; // Ensure success box is also hidden initially

    let userEmailForVerification = '';

    // --- Handle Signup Form Submission ---
    signupForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        emailErrorDiv.style.display = 'none'; // Hide previous errors on new submission

        const formData = {
            name: document.getElementById('name').value,
            phone: document.getElementById('phone').value,
            email: document.getElementById('email').value,
            password: document.getElementById('password').value,
        };

        userEmailForVerification = formData.email;

        try {
            const response = await fetch('http://127.0.0.1:5000/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData),
            });

            const result = await response.json();

            if (response.ok) {
                // If signup is successful and OTP is sent:
                signupBox.style.display = 'none';
                otpBox.style.display = 'block';
                // Optionally, show a message within the OTP box or generally
                // For now, we'll just proceed with showing the OTP box.
            } else {
                if (response.status === 409) {
                    emailErrorDiv.textContent = result.message;
                    emailErrorDiv.style.display = 'block';
                } else {
                    emailErrorDiv.textContent = result.message;
                    emailErrorDiv.style.display = 'block';
                }
            }
        } catch (error) {
            console.error('Signup Error:', error);
            emailErrorDiv.textContent = 'A network error occurred. Please try again.';
            emailErrorDiv.style.display = 'block';
        }
    });

    // --- Handle OTP Form Submission ---
    otpForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        otpErrorDiv.style.display = 'none'; // Hide previous OTP errors

        const otpValue = document.getElementById('otp').value;
        const verificationData = {
            email: userEmailForVerification,
            otp: otpValue,
        };

        try {
            const response = await fetch('http://127.0.0.1:5000/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(verificationData),
            });

            const result = await response.json();

            if (response.ok) {
                // On successful verification:
                otpBox.style.display = 'none'; // Hide the OTP box
                successBox.style.display = 'block'; // Show the success box
                successMessageDiv.textContent = result.message; // Display the success message

                // Redirect to login page after 2 seconds
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 2000);
            } else {
                // If OTP is invalid
                otpErrorDiv.textContent = result.message;
                otpErrorDiv.style.display = 'block';
            }
        } catch (error) {
            console.error('Verification Error:', error);
            otpErrorDiv.textContent = 'A network error occurred. Please try again.';
            otpErrorDiv.style.display = 'block';
        }
    });
});