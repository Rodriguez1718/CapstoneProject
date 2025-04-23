function register() {
    // Get the values from the input fields
    const firstname = document.getElementById('register-firstname').value;
    const lastname = document.getElementById('register-lastname').value;
    const phone = document.getElementById('register-phone').value;
    const address = document.getElementById('register-address').value;
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;
    
    // Check if all fields are filled
    if (!firstname || !lastname || !phone || !address || !username || !password) {
        alert("All fields are required!");
        return;
    }

    // Create the payload to send to the server
    const payload = {
        firstname: firstname,
        lastname: lastname,
        phone: phone,
        address: address,
        username: username,
        password: password
    };

    // Send a POST request to the Flask backend
    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Registration successful!") {
            alert("Registration successful! You can now log in.");
            showTab('login'); // Switch to the login tab
        } else {
            // Show error message if registration failed
            document.getElementById('register-error').style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error during registration:', error);
        document.getElementById('register-error').style.display = 'block';
    });
}

function showTab(tab) {
    // Switch between login and register tab
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    if (tab === 'login') {
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
    } else {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
    }

    // Switch tab styles
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tabElement => tabElement.classList.remove('active'));
    if (tab === 'login') {
        tabs[0].classList.add('active');
    } else {
        tabs[1].classList.add('active');
    }
}