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
