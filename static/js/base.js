class BaseManager {
    constructor() {
        this.initProjectSelector();
        console.log('BaseManager initialized');
    }

    initProjectSelector() {
        const projectSelect = document.getElementById('projet-select');
        if (projectSelect) {
            projectSelect.addEventListener('change', async (e) => {
                const projetId = e.target.value;
                try {
                    const response = await fetch('/set-projet-actif/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': this.getCsrfToken()
                        },
                        body: JSON.stringify({ projet_id: projetId })
                    });
                    
                    if (!response.ok) {
                        throw new Error('Erreur lors du changement de projet');
                    }
                    
                    const data = await response.json();
                    if (data.status === 'success') {
                        // Émettre un événement pour notifier le changement de projet
                        const event = new CustomEvent('projetChange', {
                            detail: { projetId }
                        });
                        document.dispatchEvent(event);
                        
                        this.showMessage('Projet changé avec succès', 'success');
                    } else {
                        throw new Error(data.message || 'Erreur lors du changement de projet');
                    }
                } catch (error) {
                    console.error('Erreur:', error);
                    this.showMessage('Erreur lors du changement de projet', 'error');
                }
            });
        }
    }

    getCsrfToken() {
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

    showMessage(message, type) {
        const alertsContainer = document.getElementById('alerts-container');
        if (!alertsContainer) return;

        const alert = document.createElement('div');
        alert.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        alertsContainer.appendChild(alert);
        setTimeout(() => alert.remove(), 5000);
    }
}

// Initialiser le gestionnaire de base
document.addEventListener('DOMContentLoaded', () => {
    window.baseManager = new BaseManager();
});