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

    // Dummy credentials for testing
    const storedUser = localStorage.getItem('adminUser');
    const storedPass = localStorage.getItem('adminPass');

    if (username === storedUser && password === storedPass) {
        window.location.href = "admin.html"; // Redirect to admin page
    } else {
        errorMessage.style.display = "block";
    }
}

function register() {
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    if (username && password) {
        localStorage.setItem('adminUser', username);
        localStorage.setItem('adminPass', password);
        alert('Registration successful! You can now login.');
        showTab('login');
    } else {
        alert('Please enter a valid username and password.');
    }
}

document.querySelector(".btn").addEventListener("click", function () {
    localStorage.setItem("isLoggedIn", "true"); // Set login flag
    window.location.href = "admin.html"; // Redirect to admin page
});