        // Animaciones de entrada
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