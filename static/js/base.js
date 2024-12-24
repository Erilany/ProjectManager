class BaseManager {
    constructor() {
        console.log('BaseManager initialized');
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Écouteur pour le sélecteur de projet
        const projetSelect = document.getElementById('projet-select');
        if (projetSelect) {
            projetSelect.addEventListener('change', () => this.setProjet());
        }

        // Écouteur pour les checkboxes des projets
        const projetCheckboxes = document.querySelectorAll('.projet-checkbox');
        projetCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (event) => this.handleProjetSelection(event));
        });
    }

    setProjet() {
        const projetId = document.getElementById('projet-select').value;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/set-projet-actif/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                'projet_id': projetId
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors du changement de projet');
            }
            return response.json();
        })
        .then(data => {
            window.location.reload();
        })
        .catch(error => {
            console.error('Erreur:', error);
            console.error('Détails:', error.message);
        });
    }

    handleProjetSelection(event) {
        const checkbox = event.target;
        const projetId = checkbox.value;
        const action = checkbox.checked ? 'add' : 'remove';
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch('/toggle-projet-selection/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                'projet_id': projetId,
                'action': action
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors de la mise à jour de la sélection du projet');
            }
            return response.json();
        })
        .then(data => {
            window.location.reload();
        })
        .catch(error => {
            console.error('Erreur:', error);
            checkbox.checked = !checkbox.checked;  // Rétablir l'état précédent en cas d'erreur
        });
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    const baseManager = new BaseManager();
});