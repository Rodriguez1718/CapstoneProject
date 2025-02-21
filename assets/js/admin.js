document.getElementById("addEmployeeBtn").addEventListener("click", function () {
    document.getElementById("employeeModal").style.display = "flex";
});

document.querySelector(".close").addEventListener("click", function () {
    document.getElementById("employeeModal").style.display = "none";
});

document.getElementById("employeeForm").addEventListener("submit", function (event) {
    event.preventDefault();
    alert("Employee added!");
    document.getElementById("employeeModal").style.display = "none";
});

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("employeeModal").style.display = "none";
});

document.addEventListener("DOMContentLoaded", () => {
    const employeeTable = document.getElementById("employeeTable");
    const addEmployeeBtn = document.getElementById("addEmployeeBtn");
    const employeeModal = document.getElementById("employeeModal");
    const closeModalBtn = document.querySelector(".close");
    const employeeForm = document.getElementById("employeeForm");
    const editIndex = document.getElementById("editIndex");
    const searchInput = document.getElementById("search");

    let employees = [];

    // Open modal for adding a new employee
    addEmployeeBtn.addEventListener("click", () => {
        document.getElementById("modalTitle").textContent = "Add Employee";
        employeeForm.reset();
        editIndex.value = "";
        employeeModal.style.display =
            employeeModal.style.display = "flex";
    });

    // Close modal
    closeModalBtn.addEventListener("click", () => {
        employeeModal.style.display = "none";
    });

    // Handle form submission (Add or Edit Employee)
    employeeForm.addEventListener("submit", (e) => {
        e.preventDefault();

        const name = document.getElementById("name").value;
        const role = document.getElementById("role").value;
        const email = document.getElementById("email").value;
        const phone = document.getElementById("phone").value;
        const index = editIndex.value;

        if (index === "") {
            // Add new employee
            employees.push({ name, role, email, phone });
        } else {
            // Edit existing employee
            employees[index] = { name, role, email, phone };
        }

        renderEmployees();
        employeeModal.style.display = "none";
    });

    // Render employees in table
    function renderEmployees() {
        employeeTable.innerHTML = "";
        employees.forEach((employee, index) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${employee.name}</td>
                <td>${employee.role}</td>
                <td>${employee.email}</td>
                <td>${employee.phone}</td>
                <td>
                    <button onclick="editEmployee(${index})"> Edit</button>
                    <button onclick="deleteEmployee(${index})"> Delete</button>
                </td>
            `;
            employeeTable.appendChild(row);
        });
    }

    // Edit employee
    window.editEmployee = (index) => {
        const employee = employees[index];
        document.getElementById("modalTitle").textContent = "Edit Employee";
        document.getElementById("name").value = employee.name;
        document.getElementById("role").value = employee.role;
        document.getElementById("email").value = employee.email;
        document.getElementById("phone").value = employee.phone;
        editIndex.value = index;
        employeeModal.style.display = "flex";
    };

    // Delete employee
    window.deleteEmployee = (index) => {
        if (confirm("Are you sure you want to delete this employee?")) {
            employees.splice(index, 1);
            renderEmployees();
        }
    };

    // Search employees
    window.searchEmployees = () => {
        const searchTerm = searchInput.value.toLowerCase();
        const filteredEmployees = employees.filter((emp) =>
            emp.name.toLowerCase().includes(searchTerm) ||
            emp.role.toLowerCase().includes(searchTerm) ||
            emp.email.toLowerCase().includes(searchTerm) ||
            emp.phone.toLowerCase().includes(searchTerm)
        );

        employeeTable.innerHTML = "";
        filteredEmployees.forEach((employee, index) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${employee.name}</td>
                <td>${employee.role}</td>
                <td>${employee.email}</td>
                <td>${employee.phone}</td>
                <td>
                    <button onclick="editEmployee(${index})"> Edit</button>
                    <button onclick="deleteEmployee(${index})"> Delete</button>
                </td>
            `;
            employeeTable.appendChild(row);
        });
    };

    // Logout function
    window.logout = () => {
        if (confirm("Are you sure you want to logout?")) {
            alert("Logged out successfully!");
            localStorage.removeItem("isLoggedIn");
            window.location.href = "loginAdmin.html";
            // Redirect or clear session (depending on backend)
        }
    };
});

document.addEventListener("DOMContentLoaded", function () {
    // Check if user is logged in
    if (!localStorage.getItem("isLoggedIn")) {
        window.location.href = "loginAdmin.html"; // Redirect to login if not logged in
    }

    // Prevent back navigation after logout
    window.history.pushState(null, "", window.location.href);
    window.onpopstate = function () {
        window.history.pushState(null, "", window.location.href);
    };
});

function logout() {
    localStorage.removeItem("isLoggedIn"); // Remove login state
    window.location.href = "loginAdmin.html"; // Redirect to login
}
