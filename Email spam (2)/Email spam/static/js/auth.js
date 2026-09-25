// Authentication Helpers & Demo Quick-Fill

function fillDemoUser() {
    const emailField = document.getElementById('email');
    const pwdField = document.getElementById('password');
    if (emailField && pwdField) {
        emailField.value = 'user@demo.com';
        pwdField.value = 'User@12345';
        
        // Highlight active pill
        document.getElementById('pill-user')?.classList.add('active');
        document.getElementById('pill-admin')?.classList.remove('active');

        showToast('User credentials filled! Click Sign In.', 'info');
    }
}

function fillAdminUser() {
    const emailField = document.getElementById('email');
    const pwdField = document.getElementById('password');
    if (emailField && pwdField) {
        emailField.value = 'admin@spamshield.com';
        pwdField.value = 'Admin@12345';
        
        // Highlight active pill
        document.getElementById('pill-admin')?.classList.add('active');
        document.getElementById('pill-user')?.classList.remove('active');

        showToast('Admin credentials filled! Click Sign In.', 'info');
    }
}

function togglePasswordVisibility() {
    const pwdField = document.getElementById('password');
    const eyeIcon = document.getElementById('toggle-password-icon');
    if (!pwdField) return;

    if (pwdField.type === 'password') {
        pwdField.type = 'text';
        if (eyeIcon) {
            eyeIcon.innerHTML = `
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                <line x1="1" y1="1" x2="23" y2="23"></line>
            `;
        }
    } else {
        pwdField.type = 'password';
        if (eyeIcon) {
            eyeIcon.innerHTML = `
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                <circle cx="12" cy="12" r="3"></circle>
            `;
        }
    }
}
