    document.addEventListener('DOMContentLoaded', function () {
        loadUserProfile();
        });

    function loadUserProfile() {
            const userId = localStorage.getItem('user_id');
    const username = localStorage.getItem('username');

    if (!userId) {
        showError('No hay sesión activa. Por favor inicia sesión.');
                setTimeout(() => {
        window.location.href = '/login';
                }, 2000);
    return;
            }

    fetch('/profile/', {
        method: 'POST',
    headers: {
        'Content-Type': 'application/json'
                },
    body: JSON.stringify({user_id: userId })
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Error al cargar el perfil');
                    }
    return response.json();
                })
                .then(data => {
        displayProfile(data);
                })
                .catch(error => {
        showError('Error al cargar el perfil: ' + error.message);
                });
        }

    function displayProfile(data) {
        document.getElementById('loading').style.display = 'none';
    document.getElementById('profile-content').style.display = 'block';

    // Información básica
    document.getElementById('username').textContent = data.username;
    document.getElementById('email').textContent = data.email;

    // Estadísticas
    document.getElementById('total-reviews').textContent = data.total_reviews;
    document.getElementById('avg-rating').textContent = data.average_rating ? data.average_rating.toFixed(1) : '0.0';
    document.getElementById('member-since').textContent = data.member_since;

    // Reseñas recientes
    const reviewsList = document.getElementById('recent-reviews-list');
            if (data.recent_reviews && data.recent_reviews.length > 0) {
        reviewsList.innerHTML = data.recent_reviews.map(review => `
                    <div class="review-item">
                        <div class="review-header">
                            <div>
                                <div class="review-bathroom">${review.bathroom_name}</div>
                                <div class="review-location">
                                    <i class="fas fa-map-marker-alt"></i> ${review.bathroom_location}
                                </div>
                            </div>
                            <div class="review-rating">
                                <span class="stars">${'★'.repeat(review.rating)}${'☆'.repeat(5 - review.rating)}</span>
                                <span>${review.rating}/5</span>
                            </div>
                        </div>
                        ${review.comment ? `<div class="review-comment">"${review.comment}"</div>` : ''}
                        <div class="review-date">
                            <i class="fas fa-clock"></i> ${review.created_at}
                        </div>
                    </div>
                `).join('');
            } else {
        reviewsList.innerHTML = `
                    <div style="text-align: center; padding: 2rem; color: #666;">
                        <i class="fas fa-comment-slash"></i>
                        <p>Aún no has escrito ninguna reseña.</p>
                        <a href="/catalog" class="btn btn-primary">
                            <i class="fas fa-search"></i> Explorar Baños
                        </a>
                    </div>
                `;
            }
        }

    function showError(message) {
        document.getElementById('loading').style.display = 'none';
    document.getElementById('error-message').textContent = message;
    document.getElementById('error').style.display = 'block';
        }

    function logout() {
        localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    alert('Sesión cerrada exitosamente');
    window.location.href = '/login';
        }