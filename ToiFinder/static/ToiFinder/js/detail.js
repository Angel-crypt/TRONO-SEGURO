document.addEventListener('DOMContentLoaded', function () {
    const detailContainer = document.querySelector('.detail-container');
    detailContainer.style.opacity = '0';
    detailContainer.style.transform = 'translateY(30px)';

    setTimeout(() => {
        detailContainer.style.transition = 'all 0.6s ease';
        detailContainer.style.opacity = '1';
        detailContainer.style.transform = 'translateY(0)';
    }, 100);

    // Animaciones escalonadas para las reseñas
    const reviewItems = document.querySelectorAll('.review-item');
    reviewItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(20px)';

        setTimeout(() => {
            item.style.transition = 'all 0.5s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateX(0)';
        }, 200 + (index * 100));
    });

    // Animaciones para las características
    const featureItems = document.querySelectorAll('.feature-item');
    featureItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'scale(0.9)';

        setTimeout(() => {
            item.style.transition = 'all 0.4s ease';
            item.style.opacity = '1';
            item.style.transform = 'scale(1)';
        }, 100 + (index * 50));
    });

    // Modal handling for adding review
    const addReviewBtn = document.getElementById('add-review-btn');
    const modal = document.getElementById('add-review-modal');
    const closeModal = document.querySelector('.close-modal');
    const addReviewForm = document.getElementById('add-review-form');

    function getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function openModal() {
        modal.style.display = 'block';
    }

    function closeModalFunc() {
        modal.style.display = 'none';
        addReviewForm.reset();
    }

    addReviewBtn.addEventListener('click', openModal);
    closeModal.addEventListener('click', closeModalFunc);

    // Close modal when clicking outside
    window.addEventListener('click', function (e) {
        if (e.target === modal) {
            closeModalFunc();
        }
    });

    // Handle form submission
    addReviewForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const submitButton = addReviewForm.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
        submitButton.disabled = true;

        const formData = new FormData(addReviewForm);
        const data = {
            user_id: formData.get('user_id'),
            rating: formData.get('rating'),
            comment: formData.get('comment')
        };

        try {
            const bathroomId = window.location.pathname.split('/')[2]; // Extrae bathroom_id de la URL
            const response = await fetch(`/detail/${bathroomId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            if (response.ok) {
                alert('Reseña agregada exitosamente');
                closeModalFunc();
                window.location.reload(); // Refresh to show new review
            } else {
                alert('Error al agregar la reseña: ' + result.error);
            }
        } catch (error) {
            alert('Error al conectar con el servidor');
        } finally {
            submitButton.innerHTML = originalButtonText;
            submitButton.disabled = false;
        }
    });
});

// Efectos hover mejorados
document.querySelectorAll('.action-btn').forEach(btn => {
    btn.addEventListener('mouseenter', function () {
        this.style.transform = 'translateY(-2px)';
    });

    btn.addEventListener('mouseleave', function () {
        this.style.transform = 'translateY(0)';
    });
});