class DashboardManager {
    constructor() {
        this.table = null;
        this.isUpdating = false;
        
        // Liaison des méthodes au contexte de la classe
        this.handleProjectSelection = this.handleProjectSelection.bind(this);
        this.handleSelectAll = this.handleSelectAll.bind(this);
        this.updateGlobalSelector = this.updateGlobalSelector.bind(this);
        this.updateSelectAllState = this.updateSelectAllState.bind(this);
        this.showError = this.showError.bind(this);
        
        this.init();
    }

    init() {
        this.initDataTable();
        this.initEventListeners();
        console.log('Dashboard initialized');
    }

    initDataTable() {
        this.table = $('#projectsTable').DataTable({
            language: {
                url: '/static/js/datatables-fr.json'
            },
            order: [[1, 'asc']],
            columns: [
                { orderable: false },
                null,
                null,
                null,
                null
            ],
            pageLength: 10
        });
    }

    initEventListeners() {
        document.querySelectorAll('.projet-checkbox').forEach(checkbox => {
            checkbox.removeEventListener('change', this.handleProjectSelection);
            checkbox.addEventListener('change', this.handleProjectSelection);
        });

        const selectAll = document.getElementById('selectAll');
        if (selectAll) {
            selectAll.removeEventListener('change', this.handleSelectAll);
            selectAll.addEventListener('change', this.handleSelectAll);
        }
    }

    async handleProjectSelection(event) {
        if (this.isUpdating) return;
        
        this.isUpdating = true;
        const checkbox = event.target;
        const projetId = checkbox.dataset.projetId;
        const initialState = checkbox.checked;

        try {
            console.log('Mise à jour de la sélection du projet:', projetId);
            const formData = new FormData();
            formData.append('projet_id', projetId);
            formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

            const response = await fetch('/toggle-projet-selection/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }

            const data = await response.json();

            if (data.status === 'success') {
                checkbox.checked = data.selectionne;
                console.log('Sélection mise à jour avec succès');
                await this.updateSelectedProjects();
                await this.updateGlobalSelector();
                this.updateSelectAllState();
            } else {
                checkbox.checked = initialState;
                this.showError(data.message || 'Erreur lors de la mise à jour');
            }
        } catch (error) {
            console.error('Erreur:', error);
            checkbox.checked = initialState;
            this.showError('Erreur de communication avec le serveur');
        } finally {
            this.isUpdating = false;
        }
    }

    updateSelectedProjects() {
        console.log('Mise à jour des projets sélectionnés...');
        return fetch('/get-selected-projects-content/')
        .then(response => {
            console.log('Réponse reçue:', response);
            if (!response.ok) {
                throw new Error('Erreur réseau');
            }
            return response.json();
        })
        .then(data => {
            console.log('Données reçues:', data);
            if (data.status === 'success' && data.html) {
                const container = document.getElementById('selectedProjectsContainer');
                if (container) {
                    container.innerHTML = data.html;
                    console.log('Contenu mis à jour');
                } else {
                    console.error('Conteneur non trouvé');
                }
            } else {
                console.error('Réponse invalide:', data);
            }
        })
        .catch(error => {
            console.error('Erreur lors de la mise à jour:', error);
            this.showError('Erreur lors de la mise à jour des projets sélectionnés');
        });
    }

    handleSelectAll(event) {
        const isChecked = event.target.checked;
        document.querySelectorAll('.projet-checkbox').forEach(checkbox => {
            if (checkbox.checked !== isChecked) {
                checkbox.checked = isChecked;
                checkbox.dispatchEvent(new Event('change'));
            }
        });
    }

    async updateGlobalSelector() {
        try {
            const response = await fetch('/get-selected-projects/', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.status === 'success') {
                document.querySelectorAll('.projet-selector').forEach(selector => {
                    const options = data.projets
                        .map(projet => `
                            <option value="${projet.id}" 
                                ${projet.id === data.projet_actif ? 'selected' : ''}>
                                ${projet.nom}
                            </option>
                        `).join('');
                    selector.innerHTML = options;
                });
            }
        } catch (error) {
            console.error('Erreur lors de la mise à jour du sélecteur:', error);
            this.showError('Erreur lors de la mise à jour du sélecteur');
        }
    }

    updateSelectAllState() {
        const selectAll = document.getElementById('selectAll');
        if (selectAll) {
            const checkboxes = document.querySelectorAll('.projet-checkbox');
            const allChecked = Array.from(checkboxes).every(cb => cb.checked);
            selectAll.checked = allChecked;
        }
    }

    showError(message) {
        const alertsContainer = document.getElementById('alerts-container');
        if (alertsContainer) {
            const alert = document.createElement('div');
            alert.className = 'alert alert-danger alert-dismissible fade show';
            alert.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            alertsContainer.insertBefore(alert, alertsContainer.firstChild);
        }
    }
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardManager = new DashboardManager();
});