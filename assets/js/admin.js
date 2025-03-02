document.addEventListener("DOMContentLoaded", function () {
    if (localStorage.getItem("role") !== "admin") {
        alert("Access Denied: You are not an admin!");
        window.location.href = "/loginAdmin"; // Redirect to login page
    }
});

document.getElementById("addPetBtn").addEventListener("click", function () {
    document.getElementById("petModal").classList.add("active");
});

document.querySelector(".close").addEventListener("click", function () {
    document.getElementById("petModal").classList.remove("active");
});

// Form for pet addition
document.getElementById("petForm").addEventListener("submit", function (event) {
    event.preventDefault();

    const petName = document.getElementById("petName").value;
    const petAge = document.getElementById("petAge").value;
    const petSex = document.getElementById("petSex").value;
    const petShelter = document.getElementById("petShelter").value;
    const petImage = document.getElementById("petImage").files[0]; // Get the image file

    const formData = new FormData();
    formData.append("name", petName);
    formData.append("age", petAge);
    formData.append("sex", petSex);
    formData.append("shelter", petShelter);
    formData.append("image", petImage);

    fetch("/add_pet", {
        method: "POST",
        body: formData, // Use FormData for image upload
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
                document.getElementById("petModal").style.display = "none";
                fetchPets(); // Refresh pet list
            } else {
                alert("Error adding pet.");
            }
        })
        .catch(error => console.error("Error:", error));
});


// Logout function
window.logout = () => {
    if (confirm("Are you sure you want to logout?")) {
        fetch('/logout', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => {
                if (response.ok) {
                    alert("Logged out successfully!");
                    localStorage.removeItem("isLoggedIn");
                    sessionStorage.clear();
                    window.location.href = "/loginAdmin";
                } else {
                    alert("Logout failed. Please try again.");
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert("An error occurred. Please try again.");
            });
    }
};

// Prevent Back Navigation After Logout
window.addEventListener("load", function () {
    if (!localStorage.getItem("isLoggedIn")) {
        window.location.href = "/loginAdmin"; // Redirect if not logged in
    }
    window.history.pushState(null, "", window.location.href);
    window.onpopstate = function () {
        window.history.pushState(null, "", window.location.href);
    };
});

document.addEventListener("DOMContentLoaded", function () {
    fetchAdminDashboard();
});

function fetchAdminDashboard() {
    fetch("/admin/data")
        .then(response => response.json())
        .then(data => {
            displayStats(data.stats);
            displayAdoptions(data.adoptions);
            displayApplications(data.applications);
            displayBusinesses(data.businesses);
            displayPets(data.pets);
            displayTransactions(data.transactions);
        })
        .catch(error => console.error("Error fetching admin data:", error));
}

function displayStats(stats) {
    document.getElementById("totalAdoptions").textContent = stats.totalAdoptions;
    document.getElementById("pendingApplications").textContent = stats.pendingApplications;
    document.getElementById("totalBusinesses").textContent = stats.totalBusinesses;
    document.getElementById("availablePets").textContent = stats.availablePets;
}

function displayAdoptions(adoptions) {
    const table = document.getElementById("adoptionRecords");
    table.innerHTML = adoptions.map(a => `
        <tr>
            <td>${a.adopter}</td>
            <td>${a.pet}</td>
            <td>${a.date}</td>
        </tr>
    `).join("");
}

function displayApplications(applications) {
    const table = document.getElementById("adoptionApplications");
    table.innerHTML = applications.map(a => `
        <tr>
            <td>${a.adopter}</td>
            <td>${a.pet}</td>
            <td>${a.status}</td>
            <td><button onclick="approveApplication(${a.id})">Approve</button></td>
        </tr>
    `).join("");
}

function approveApplication(id) {
    fetch(`/approve_application/${id}`, { method: "POST" })
        .then(response => response.json())
        .then(() => fetchAdminDashboard())
        .catch(error => console.error("Error approving application:", error));
}

function displayBusinesses(businesses) {
    const table = document.getElementById("businessList");
    table.innerHTML = businesses.map(b => `
        <tr>
            <td>${b.name}</td>
            <td>${b.category}</td>
            <td>${b.contact}</td>
        </tr>
    `).join("");
}

// Fetch pets and update table
function fetchPets() {
    fetch("/pets")
        .then(response => response.json())
        .then(data => {
            const table = document.getElementById("petTable");
            table.innerHTML = data.map(pet => `
                <tr>
                    <td><img src="${pet.image || '/assets/default-pet.jpg'}" width="50" alt="Pet Image"></td>
                    <td>${encodeHTML(pet.name) || "N/A"}</td>
                    <td>${pet.age || "N/A"}</td>
                    <td>${encodeHTML(pet.sex) || "N/A"}</td>
                    <td>${encodeHTML(pet.shelter) || "N/A"}</td>
                    <td>${encodeHTML(pet.status) || "N/A"}</td>
                    <td>
                        <button onclick="editPet(${pet.id})">Edit</button>
                        <button onclick="deletePet(${pet.id})">Delete</button>
                    </td>
                </tr>
            `).join("");
        })
        .catch(error => console.error("Error fetching pets:", error));
}

// Function to prevent XSS attacks
function encodeHTML(str) {
    return str ? str.replace(/</g, "&lt;").replace(/>/g, "&gt;") : "";
}

// Edit Pet
function editPet(id) {
    fetch(`/pet/${id}`)
        .then(response => response.json())
        .then(pet => {
            document.getElementById("editPetId").value = pet.id;
            document.getElementById("petName").value = pet.name;
            document.getElementById("petAge").value = pet.age;
            document.getElementById("petSex").value = pet.sex;
            document.getElementById("petShelter").value = pet.shelter;
            document.getElementById("petModal").style.display = "block";
        });
}

// Delete Pet
function deletePet(id) {
    if (confirm("Are you sure you want to delete this pet?")) {
        fetch(`/delete_pet/${id}`, { method: "DELETE" })
            .then(response => {
                if (response.ok) {
                    alert("Pet deleted successfully!");
                    loadPets();
                } else {
                    alert("Error deleting pet.");
                }
            });
    }
}

document.addEventListener("DOMContentLoaded", fetchPets);

function displayTransactions(transactions) {
    const table = document.getElementById("transactionList");
    table.innerHTML = transactions.map(t => `
        <tr>
            <td>${t.business}</td>
            <td>${t.amount}</td>
            <td>${t.date}</td>
        </tr>
    `).join("");
}

document.addEventListener('DOMContentLoaded', () => {
    // Handle section visibility and navigation
    const sections = document.querySelectorAll('main section');
    const navLinks = document.querySelectorAll('nav a');

    // Initially hide all sections except overview
    sections.forEach(section => {
        if (section.id !== 'overview') {
            section.style.display = 'none';
        }
    });

    // Function to show section
    const showSection = (sectionId) => {
        sections.forEach(section => {
            if (section.id === sectionId) {
                section.style.display = 'block';
                section.style.opacity = '1';
                section.classList.add('section-enter-active');
            } else {
                section.style.display = 'none';
                section.classList.remove('section-enter-active');
            }
        });
    };

    // Handle navigation clicks
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();

            // Remove active class from all links
            navLinks.forEach(nav => nav.classList.remove('active'));

            // Add active class to clicked link
            link.classList.add('active');

            // Get the section id from href
            const sectionId = link.getAttribute('href').substring(1);

            // Show the selected section
            showSection(sectionId);
        });
    });

    // Handle initial hash in URL
    if (window.location.hash) {
        const sectionId = window.location.hash.substring(1);
        const activeLink = document.querySelector(`nav a[href="#${sectionId}"]`);
        if (activeLink) {
            // Remove active class from all links
            navLinks.forEach(nav => nav.classList.remove('active'));
            // Add active class to current link
            activeLink.classList.add('active');
            // Show the section
            showSection(sectionId);
        }
    }
});
