class SummaryManager {
    constructor() {
        this.initEventListeners();
        
        // Charger le contenu initial
        this.loadSummaryContent();
        
        console.log('SummaryManager initialized');
    }

    loadSummaryContent() {
        fetch('/summary/content/')
            .then(async response => {
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || 'Erreur serveur');
                }
                return response.json();
            })
            .then(contentData => {
                if (contentData.html) {
                    const container = document.querySelector('#summary-content');
                    if (container) {
                        container.innerHTML = contentData.html;
                        this.initEventListeners();
                    }
                    
                    // Mettre à jour le titre si nécessaire
                    if (contentData.projet_nom) {
                        const titleElement = document.querySelector('.container-fluid h1.h3');
                        if (titleElement) {
                            titleElement.textContent = `Synthèse - ${contentData.projet_nom}`;
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Erreur lors du chargement:', error);
                const container = document.querySelector('#summary-content');
                if (container) {
                    container.innerHTML = `
                        <div class="alert alert-danger">
                            Une erreur est survenue lors du chargement des données.
                            Veuillez réessayer ou contacter l'administrateur si le problème persiste.
                        </div>
                    `;
                }
            });
    }

    initEventListeners() {
        // Gérer le changement de projet
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
                        // Recharger le contenu
                        this.loadSummaryContent();
                    } else {
                        this.showMessage('Erreur lors du changement de projet', 'error');
                    }
                } catch (error) {
                    console.error('Erreur:', error);
                    this.showMessage('Erreur lors du changement de projet', 'error');
                }
            });
        }

        // Gérer les changements de sélection d'étapes
        document.querySelectorAll('.processus-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', async (e) => {
                const etapeId = e.target.dataset.etapeId;
                const selected = e.target.checked;
                const etapeElement = e.target.closest('.processus-etape');
                
                try {
                    const response = await fetch('/summary/toggle_etape/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': this.getCsrfToken()
                        },
                        body: JSON.stringify({
                            etape_id: etapeId,
                            selected: selected
                        })
                    });

                    if (!response.ok) {
                        throw new Error('Erreur réseau');
                    }

                    const data = await response.json();
                    if (data.status === 'success') {
                        etapeElement.classList.toggle('selected', selected);
                        this.showMessage('Modification enregistrée', 'success');
                    } else {
                        e.target.checked = !selected;
                        etapeElement.classList.toggle('selected', !selected);
                        this.showMessage('Erreur lors de la mise à jour', 'error');
                    }
                } catch (error) {
                    console.error('Erreur:', error);
                    e.target.checked = !selected;
                    etapeElement.classList.toggle('selected', !selected);
                    this.showMessage('Erreur lors de la mise à jour', 'error');
                }
            });
        });
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }

    showMessage(message, type) {
        const alertsContainer = document.getElementById('alerts-container');
        if (!alertsContainer) return;

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        alertsContainer.innerHTML = '';
        alertsContainer.appendChild(alertDiv);
        setTimeout(() => alertDiv.remove(), 3000);
    }
}

// Initialiser le gestionnaire de synthèse
document.addEventListener('DOMContentLoaded', () => {
    window.summaryManager = new SummaryManager();
});