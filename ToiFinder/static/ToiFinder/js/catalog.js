document.addEventListener('DOMContentLoaded', function () {
    // Cache DOM elements
    const cards = document.querySelectorAll('.bathroom-card');
    const filterForm = document.getElementById('filterForm');
    const submitBtn = filterForm.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerHTML;

    // Optimized card animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const cardObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Initialize card animations
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;

        cardObserver.observe(card);

        // Enhanced hover effects
        card.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-8px) scale(1.02)';
            this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            this.style.boxShadow = '0 20px 40px rgba(0,0,0,0.1)';
        });

        card.addEventListener('mouseleave', function () {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '';
        });
    });

    // Optimized form handling
    let searchTimeout;
    const searchInput = document.getElementById('search');

    searchInput.addEventListener('input', function () {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            if (this.value.length > 2 || this.value.length === 0) {
                filterForm.submit();
            }
        }, 500);
    });

    // Enhanced form submission
    filterForm.addEventListener('submit', function (e) {
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Buscando...';
        submitBtn.disabled = true;
        // Re-enable after timeout as fallback
        setTimeout(() => {
            submitBtn.innerHTML = originalBtnText;
            submitBtn.disabled = false;
        }, 5000);
    });

    // Smooth pagination scrolling
    const paginationLinks = document.querySelectorAll('.pagination a');
    paginationLinks.forEach(link => {
        link.addEventListener('click', function () {
            const catalogSection = document.querySelector('.catalog-section');
            if (catalogSection) {
                window.scrollTo({
                    top: catalogSection.offsetTop - 100,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Keyboard navigation
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            const activeElement = document.activeElement;
            if (activeElement.tagName === 'INPUT' || activeElement.tagName === 'SELECT') {
                activeElement.blur();
            }
        }
    });
});