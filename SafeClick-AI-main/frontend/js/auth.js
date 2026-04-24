/**
 * Auth Module — ThreatSense AI
 * Handles login, signup, anonymous sign-in, and auth state routing.
 */

(function () {
    const isLoginPage = window.location.pathname.endsWith('index.html') ||
        window.location.pathname.endsWith('/') ||
        window.location.pathname === '';

    // ── Auth State Listener ──
    auth.onAuthStateChanged((user) => {
        if (user) {
            // User is signed in → go to dashboard
            if (isLoginPage) {
                window.location.href = 'dashboard.html';
            }
        } else {
            // Not signed in → show login or redirect
            if (isLoginPage) {
                document.getElementById('loading-overlay').classList.add('hidden');
                document.getElementById('login-page').classList.remove('hidden');
            } else {
                window.location.href = 'index.html';
            }
        }
    });

    // Only wire up login form on the login page
    if (!isLoginPage) return;

    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const emailError = document.getElementById('email-error');
    const passwordError = document.getElementById('password-error');
    const btnSignIn = document.getElementById('btn-signin');
    const btnSignUp = document.getElementById('btn-signup');
    const btnAnonymous = document.getElementById('btn-anonymous');

    // ── Validation ──
    function validateForm() {
        let valid = true;
        emailError.classList.add('hidden');
        passwordError.classList.add('hidden');

        const email = emailInput.value.trim();
        const password = passwordInput.value;

        if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            emailError.textContent = 'Please enter a valid email address.';
            emailError.classList.remove('hidden');
            valid = false;
        }

        if (!password || password.length < 6) {
            passwordError.textContent = 'Password must be at least 6 characters.';
            passwordError.classList.remove('hidden');
            valid = false;
        }

        return valid;
    }

    function setLoading(loading) {
        btnSignIn.disabled = loading;
        btnSignUp.disabled = loading;
        btnAnonymous.disabled = loading;
        emailInput.disabled = loading;
        passwordInput.disabled = loading;

        if (loading) {
            btnSignIn.innerHTML = '<span class="spinner"></span> Signing In...';
            btnSignUp.innerHTML = '<span class="spinner"></span> Signing Up...';
        } else {
            btnSignIn.textContent = 'Sign In';
            btnSignUp.textContent = 'Sign Up';
        }
    }

    function showError(msg) {
        passwordError.textContent = msg;
        passwordError.classList.remove('hidden');
    }

    // ── Sign In ──
    btnSignIn.addEventListener('click', async () => {
        if (!validateForm()) return;
        setLoading(true);
        try {
            await auth.signInWithEmailAndPassword(emailInput.value.trim(), passwordInput.value);
            // onAuthStateChanged will redirect
        } catch (err) {
            setLoading(false);
            showError(err.message);
        }
    });

    // ── Sign Up ──
    btnSignUp.addEventListener('click', async () => {
        if (!validateForm()) return;
        setLoading(true);
        try {
            await auth.createUserWithEmailAndPassword(emailInput.value.trim(), passwordInput.value);
            // onAuthStateChanged will redirect
        } catch (err) {
            setLoading(false);
            showError(err.message);
        }
    });

    // ── Anonymous ──
    btnAnonymous.addEventListener('click', async () => {
        setLoading(true);
        try {
            await auth.signInAnonymously();
            // onAuthStateChanged will redirect
        } catch (err) {
            setLoading(false);
            showError(err.message);
        }
    });

    // Allow Enter key to submit
    passwordInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') btnSignIn.click();
    });
})();
