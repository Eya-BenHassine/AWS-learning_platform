// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Markdown editor for module content (if needed)
    const moduleTextarea = document.getElementById('module-content');
    if (moduleTextarea) {
        // Simple markdown preview toggle
        const previewBtn = document.createElement('button');
        previewBtn.type = 'button';
        previewBtn.className = 'btn btn-sm btn-outline-secondary mt-2';
        previewBtn.innerHTML = '<i class="fas fa-eye"></i> Preview';
        previewBtn.onclick = function() {
            const content = moduleTextarea.value;
            const preview = document.getElementById('content-preview');
            if (preview) {
                preview.innerHTML = marked.parse(content);
                preview.classList.toggle('d-none');
            }
        };
        moduleTextarea.parentNode.appendChild(previewBtn);
    }
    
    // Progress tracking
    function updateProgressBar() {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            const targetWidth = bar.getAttribute('aria-valuenow') || bar.style.width;
            bar.style.width = targetWidth;
            bar.textContent = targetWidth;
        });
    }
    
    // Course enrollment confirmation
    const enrollForms = document.querySelectorAll('form[action*="enroll"]');
    enrollForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!this.classList.contains('confirmed')) {
                e.preventDefault();
                if (confirm('Are you sure you want to enroll in this course?')) {
                    this.classList.add('confirmed');
                    this.submit();
                }
            }
        });
    });
    
    // Module completion tracking
    const completeButtons = document.querySelectorAll('form[action*="complete"] button');
    completeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const moduleTitle = this.closest('.module-page').querySelector('h1').textContent;
            localStorage.setItem(`completed_${moduleTitle}`, new Date().toISOString());
            
            // Show completion animation
            this.innerHTML = '<i class="fas fa-check"></i> Completed!';
            this.classList.remove('btn-success');
            this.classList.add('btn-secondary');
            this.disabled = true;
        });
    });
    
    // Search functionality
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (this.value.length >= 3 || this.value.length === 0) {
                    this.closest('form').submit();
                }
            }, 500);
        });
    }
    
    // Dark/Light theme toggle (optional)
    const themeToggle = document.createElement('button');
    themeToggle.className = 'btn btn-sm btn-outline-secondary position-fixed';
    themeToggle.style.bottom = '20px';
    themeToggle.style.right = '20px';
    themeToggle.style.zIndex = '1000';
    themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    themeToggle.title = 'Toggle theme';
    themeToggle.onclick = function() {
        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-bs-theme', newTheme);
        this.innerHTML = newTheme === 'dark' ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
        localStorage.setItem('theme', newTheme);
    };
    
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
    document.body.appendChild(themeToggle);
    
    // Initialize animations on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // Observe elements with animation classes
    document.querySelectorAll('.card, .feature-card, .course-card').forEach(el => {
        observer.observe(el);
    });
    
    // Update user activity
    function updateLastActivity() {
        if (typeof userId !== 'undefined') {
            // In a real app, you would send this to your backend
            localStorage.setItem('last_activity', new Date().toISOString());
        }
    }
    
    // Update activity every 30 seconds
    setInterval(updateLastActivity, 30000);
    
    // Initialize on page load
    updateProgressBar();
    updateLastActivity();
    
    // Console welcome message
    console.log('%c🚀 AWS Learning Platform', 'font-size: 20px; font-weight: bold; color: #667eea;');
    console.log('%cWelcome to our AWS learning platform!', 'color: #94a3b8;');
});