function showTab(tab) {
    document.getElementById('login-form').style.display = tab === 'login' ? 'block' : 'none';
    document.getElementById('register-form').style.display = tab === 'register' ? 'block' : 'none';

    let tabs = document.querySelectorAll('.tab');
    tabs.forEach(t => t.classList.remove('active'));

    if (tab === 'login') {
        tabs[0].classList.add('active');
    } else {
        tabs[1].classList.add('active');
    }
}

function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    const errorMessage = document.getElementById('login-error');

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: username, password: password })
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                localStorage.setItem("isLoggedIn", true); // Store login state
                window.location.href = data.redirect; // Redirect to admin page
            } else {
                errorMessage.style.display = "block";
            }
        })
        .catch(error => {
            console.error('Error:', error);
            errorMessage.style.display = "block";
        });
}

function register() {
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: username, password: password })
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert('Registration successful! You can now login.');
                showTab('login');
            } else {
                alert(data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
}