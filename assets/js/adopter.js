// Updated JavaScript for adopter.html

function logout() {
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
                    localStorage.removeItem("role");
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
}

document.addEventListener("DOMContentLoaded", function () {
    loadStores();

    // Handle sidebar show/hide
    const menuButton = document.querySelector('.menu-button');
    const sidebar = document.querySelector('.side-bar');
    const logoutButton = document.getElementById('logout-button');

    menuButton.addEventListener('click', showSidebar);
    logoutButton.addEventListener('click', logout);

    function showSidebar() {
        sidebar.style.display = 'flex';
    }

    function hideSidebar() {
        sidebar.style.display = 'none';
    }

});

// Fetch pets and update display
function fetchPets() {
    fetch("/pets")
        .then(response => response.json())
        .then(data => {
            const petContainer = document.getElementById("petContainer");
            petContainer.innerHTML = data.map(pet => `
                <div class="pet-card">
                    <img src="${pet.image || '/assets/default-pet.jpg'}" alt="Pet Image">
                    <h3>${encodeHTML(pet.name) || "Unnamed Pet"}</h3>
                    <p><strong>Age:</strong> ${pet.age || "Unknown"}</p>
                    <p><strong>Sex:</strong> ${encodeHTML(pet.sex) || "Unknown"}</p>
                    <p><strong>Shelter:</strong> ${encodeHTML(pet.shelter) || "Not specified"}</p>
                    <p><strong>Status:</strong> ${encodeHTML(pet.status) || "Available"}</p>
                    <button onclick="adoptPet(${pet.id})">Adopt</button>
                </div>
            `).join("");
        })
        .catch(error => console.error("Error fetching pets:", error));
}

// Function to prevent XSS attacks
function encodeHTML(str) {
    return str ? str.replace(/</g, "&lt;").replace(/>/g, "&gt;") : "";
}

document.addEventListener("DOMContentLoaded", fetchPets);

function loadStores() {
    fetch("/api/stores")
        .then(response => response.json())
        .then(data => {
            const storesContainer = document.getElementById("store-list");
            storesContainer.innerHTML = "";
            data.forEach(store => {
                const storeCard = document.createElement("div");
                storeCard.classList.add("card");
                storeCard.innerHTML = `
                    <img src="${store.image}" alt="${store.name}">
                    <div class="card-content">
                        <h3>${store.name}</h3>
                        <p>Category: ${store.category}</p>
                        <p>Location: ${store.location}</p>
                        <button onclick="visitStore(${store.id})">Visit</button>
                    </div>
                `;
                storesContainer.appendChild(storeCard);
            });
        });
}

function adoptPet(petId) {
    alert(`Adoption request for pet ID: ${petId} sent!`);
}

function visitStore(storeId) {
    alert(`Redirecting to store ID: ${storeId}`);
}

const toggleButton = document.getElementById('toggle-btn')
const sidebar = document.getElementById('sidebar')

function toggleSideBar() {
    sidebar.classList.toggle('close')
    toggleButton.classList.toggle('rotate');

    closeAllSubMenus()
}

function toggleSubMenu(button) {
    if (!button.nextElementSibling.classList.contains('show')) {
        closeAllSubMenus()
    }

    button.nextElementSibling.classList.toggle('show')
    button.classList.toggle('rotate')

    if (sidebar.classList.contains('close')) {
        sidebar.classList.toggle('close')
        toggleButton.classList.toggle('rotate')
    }
}

function closeAllSubMenus() {
    Array.from(sidebar.getElementsByClassName('show')).forEach(ul => {
        ul.classList.remove('show')
        ul.previousElementSibling.classList.remove('rotate')
    })
}

document.addEventListener("DOMContentLoaded", function () {
    let lastScrollY = window.scrollY;
    const topbar = document.getElementById("topbar");

    function handleScroll() {
        if (window.scrollY > 0) {
            topbar.classList.add("scrolled");
        } else {
            topbar.classList.remove("scrolled");
        }

        if (window.scrollY > lastScrollY) {
            topbar.classList.add("hidden");
        } else {
            topbar.classList.remove("hidden");
        }
        lastScrollY = window.scrollY;
    }

    window.addEventListener("scroll", handleScroll);
    handleScroll(); // Run on load
});

document.addEventListener("DOMContentLoaded", function () {
    const menuBtn = document.getElementById("menu-btn")
    const navLinks = document.getElementById("nav-links")

    menuBtn.addEventListener("click", function () {
        navLinks.classList.toggle("active")
    })
})

function showSidebar() {
    const sidebar = document.querySelector('.side-bar')
    sidebar.style.display = 'flex'
}

function hideSidebar() {
    const sidebar = document.querySelector('.side-bar')
    sidebar.style.display = 'none'
}