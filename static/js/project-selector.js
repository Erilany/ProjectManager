class ProjectSelector {
    constructor() {
        this.selector = document.querySelector('.projet-selector');
        this.init();
    }

    init() {
        if (this.selector) {
            this.selector.addEventListener('change', this.handleProjectChange.bind(this));
        }
    }

    async handleProjectChange(event) {
        const selectedProjectId = event.target.value;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        try {
            const response = await fetch('/set-projet-actif/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    projet_id: selectedProjectId
                })
            });
            const data = await response.json();

            if (data.status === 'success') {
                // Si nous sommes sur la page Organization, mettre à jour le contenu sans recharger
                const isOrganizationPage = window.location.pathname.includes('/organization');
                if (isOrganizationPage) {
                    await this.updateOrganizationContent();
                } else {
                    // Pour les autres pages, recharger normalement
                    window.location.reload();
                }
            } else {
                console.error('Erreur lors de la mise à jour du projet:', data.message);
                this.showError('Erreur lors de la mise à jour du projet');
            }
        } catch (error) {
            console.error('Erreur:', error);
            this.showError('Erreur lors de la mise à jour du projet');
        }
    }

    async updateOrganizationContent() {
        try {
            const response = await fetch('/organization/content/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'text/html'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const html = await response.text();
            
            // Mettre à jour le contenu principal
            const contentContainer = document.querySelector('.container-fluid');
            if (!contentContainer) {
                throw new Error('Container principal non trouvé');
            }

            // Sauvegarder les modales avant la mise à jour
            const modalInterlocuteur = document.getElementById('interlocuteurModal');
            const modalGroupe = document.getElementById('groupeModal');

            // Mettre à jour le contenu
            contentContainer.innerHTML = html;

            // Restaurer les modales
            if (modalInterlocuteur) {
                document.body.appendChild(modalInterlocuteur);
            }
            if (modalGroupe) {
                document.body.appendChild(modalGroupe);
            }

            // Réinitialiser les gestionnaires d'événements
            if (window.organizationManager) {
                window.organizationManager = new OrganizationManager();
            }
        } catch (error) {
            console.error('Erreur lors de la mise à jour du contenu:', error);
            this.showError('Erreur lors de la mise à jour du contenu');
        }
    }

    showError(message) {
        const alertContainer = document.getElementById('alerts-container') || document.querySelector('.container-fluid');
        if (alertContainer) {
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-danger alert-dismissible fade show';
            alertDiv.role = 'alert';
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            alertContainer.insertBefore(alertDiv, alertContainer.firstChild);
        }
    }
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    window.projectSelector = new ProjectSelector();
});
