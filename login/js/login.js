// --- Element Selection ---
const loginBox = document.getElementById('login');
const forgotBox1 = document.getElementById('forgot');
const forgotBox2 = document.getElementById('forgot2');
const forgotBox3 = document.getElementById('forgot3');

const loginForm = document.getElementById('login-form');
const forgotEmailForm = document.getElementById('forgot-email-form');
const forgotOtpForm = document.getElementById('forgot-otp-form');
const forgotPassForm = document.getElementById('forgot-pass-form');

const errorDivs = {
    login: document.getElementById('login-error'),
    forgotEmail: document.getElementById('forgot-email-error'),
    forgotOtp: document.getElementById('forgot-otp-error'),
    forgotPass: document.getElementById('forgot-pass-error')
};

// --- State Variables ---
let emailForReset = '';
let otpForReset = '';

// --- UI Navigation Functions ---
function hideAll() {
    loginBox.style.display = 'none';
    forgotBox1.style.display = 'none';
    forgotBox2.style.display = 'none';
    forgotBox3.style.display = 'none';
}

function toForgotPass() {
    hideAll();
    forgotBox1.style.display = 'block';
}

function backToLogin() {
    hideAll();
    loginBox.style.display = 'block';
}

// --- Error Handling ---
function showError(form, message) {
    errorDivs[form].textContent = message;
    errorDivs[form].style.display = 'block';
}

function hideError(form) {
    errorDivs[form].style.display = 'none';
}

// --- Form Submit Event Listeners ---

// 1. Login Form
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError('login');
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const response = await fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
    });
    const result = await response.json();
    if (response.ok) {
        alert(result.message);
        window.location.href = '../index.html'; // Or wherever your main page is
    } else {
        showError('login', result.message);
    }
});

// 2. Forgot Password - Send OTP
forgotEmailForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError('forgotEmail');
    emailForReset = document.getElementById('emailForgot').value;

    const response = await fetch('http://127.0.0.1:5000/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: emailForReset }),
    });
    const result = await response.json();
    if (response.ok) {
        alert(result.message); // Inform user to check email
        hideAll();
        forgotBox2.style.display = 'block';
    } else {
        showError('forgotEmail', result.message);
    }
});

// 3. Forgot Password - Verify OTP
forgotOtpForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError('forgotOtp');
    otpForReset = document.getElementById('otp').value;

    const response = await fetch('http://127.0.0.1:5000/verify-reset-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: emailForReset, otp: otpForReset }),
    });
    const result = await response.json();
    if (response.ok) {
        hideAll();
        forgotBox3.style.display = 'block';
    } else {
        showError('forgotOtp', result.message);
    }
});

// 4. Forgot Password - Set New Password
forgotPassForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError('forgotPass');
    const newPassword = document.getElementById('newPassword').value;
    const confPassword = document.getElementById('confPassword').value;

    if (newPassword !== confPassword) {
        showError('forgotPass', 'Passwords do not match.');
        return;
    }

    const response = await fetch('http://127.0.0.1:5000/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            email: emailForReset,
            otp: otpForReset,
            password: newPassword
        }),
    });
    const result = await response.json();
    if (response.ok) {
        alert(result.message);
        backToLogin();
    } else {
        showError('forgotPass', result.message);
    }
});