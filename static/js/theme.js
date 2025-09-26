// Theme toggle functionality
const htmlElement = document.documentElement;
const themeToggle = document.getElementById('themeToggle');
const themeToggleDropdown = document.getElementById('themeToggleDropdown');
const themeIcon = document.getElementById('themeIcon');
const themeIconDropdown = document.getElementById('themeIconDropdown');
const themeText = document.getElementById('themeText');
const themeTextDropdown = document.getElementById('themeTextDropdown');

// Get saved theme from localStorage
const savedTheme = localStorage.getItem('theme') || 'light';

// Apply theme function
function applyTheme(theme) {
    if (theme === 'dark') {
        htmlElement.setAttribute('data-theme', 'dark');
        // Update main theme toggle (for non-authenticated users)
        if (themeIcon) {
            themeIcon.className = 'bi bi-moon-fill';
        }
        if (themeText) {
            themeText.textContent = 'Escuro';
        }
        // Update dropdown theme toggle (for authenticated users)
        if (themeIconDropdown) {
            themeIconDropdown.className = 'bi bi-moon-fill me-2';
        }
        if (themeTextDropdown) {
            themeTextDropdown.textContent = 'Tema Escuro';
        }
    } else {
        htmlElement.removeAttribute('data-theme');
        // Update main theme toggle (for non-authenticated users)
        if (themeIcon) {
            themeIcon.className = 'bi bi-sun-fill';
        }
        if (themeText) {
            themeText.textContent = 'Claro';
        }
        // Update dropdown theme toggle (for authenticated users)
        if (themeIconDropdown) {
            themeIconDropdown.className = 'bi bi-sun-fill me-2';
        }
        if (themeTextDropdown) {
            themeTextDropdown.textContent = 'Tema Claro';
        }
    }
}

// Apply theme on page load
applyTheme(savedTheme);

// Toggle theme function
function toggleTheme() {
    const currentTheme = htmlElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    applyTheme(newTheme);
    localStorage.setItem('theme', newTheme);
}

// Add event listeners to both toggle buttons
if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
}
if (themeToggleDropdown) {
    themeToggleDropdown.addEventListener('click', toggleTheme);
}
