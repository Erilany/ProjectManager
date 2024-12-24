document.addEventListener('DOMContentLoaded', function() {
    const projetSelector = document.querySelector('.projet-selector');
    
    // Charger le dernier projet sélectionné au démarrage
    const lastSelectedProject = localStorage.getItem('lastSelectedProject');
    if (lastSelectedProject) {
        projetSelector.value = lastSelectedProject;
        // Déclencher le changement pour mettre à jour la session
        const event = new Event('change');
        projetSelector.dispatchEvent(event);
    }

    projetSelector.addEventListener('change', function(e) {
        const projetId = this.value;
        
        // Sauvegarder dans localStorage
        localStorage.setItem('lastSelectedProject', projetId);
        
        fetch('/set-projet-actif/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                projet_id: projetId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload();
            }
        });
    });
});