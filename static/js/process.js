$(document).ready(function() {
    console.log('=== JQUERY EST PRÊT ===');
    
    // Gestion du clic sur le bouton Enregistrer
    $('.save-subtask-btn').on('click', function() {
        const modal = $(this).closest('.modal');
        const form = modal.find('form');
        form.submit();
    });
    
    // Gestion de la soumission du formulaire
    $('.subtask-form').on('submit', function(e) {
        e.preventDefault();
        console.log('SOUMISSION DU FORMULAIRE !');
        
        const form = $(this);
        const actionId = form.find('input[name="action_id"]').val();
        
        // Récupération des valeurs du formulaire
        const formData = {
            action_id: actionId,
            subject: form.find('input[name="subject"]').val(),
            comments: form.find('textarea[name="comments"]').val(),
            start_date: form.find('input[name="start_date"]').val(),
            end_date: form.find('input[name="end_date"]').val(),
            status: form.find('select[name="status"]').val(),
            is_private: form.find('input[name="is_private"]').is(':checked'),
            in_planning: form.find('input[name="in_planning"]').is(':checked')
        };
        
        // Vérification des données
        if (!formData.subject) {
            alert('Le sujet de la sous-tâche est requis !');
            return;
        }
        
        // Récupération du token CSRF
        const csrftoken = form.find('input[name="csrfmiddlewaretoken"]').val();
        
        // Envoi des données au serveur
        $.ajax({
            url: '/process/save_subtask/',
            type: 'POST',
            dataType: 'json',
            data: formData,
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function(response) {
                console.log('Succès:', response);
                alert('Sous-tâche enregistrée avec succès !');
                
                // Fermer le modal
                modal.modal('hide');
                
                // Réinitialiser le formulaire
                form[0].reset();
                
                // Recharger le contenu
                location.reload();
            },
            error: function(xhr, status, error) {
                console.error('Erreur:', error);
                alert('Erreur lors de l\'enregistrement de la sous-tâche');
            }
        });
    });
    
    // Gestion du clic sur les badges de statut
    $('.status-badge').on('click', function() {
        const subtaskId = $(this).data('subtask-id');
        const currentStatus = $(this).data('status');
        const nextStatus = getNextStatus(currentStatus);
        
        updateSubtaskStatus(subtaskId, nextStatus);
    });
    
    // Fonction pour obtenir le prochain statut
    function getNextStatus(currentStatus) {
        const statusOrder = ['todo', 'in-progress', 'waiting', 'done'];
        const currentIndex = statusOrder.indexOf(currentStatus);
        return statusOrder[(currentIndex + 1) % statusOrder.length];
    }
    
    // Fonction pour mettre à jour le statut d'une sous-tâche
    function updateSubtaskStatus(subtaskId, newStatus) {
        const csrftoken = $('input[name="csrfmiddlewaretoken"]').first().val();
        
        $.ajax({
            url: '/process/update_subtask_status/',
            type: 'POST',
            dataType: 'json',
            data: {
                subtask_id: subtaskId,
                status: newStatus
            },
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function(response) {
                location.reload();
            },
            error: function(xhr, status, error) {
                console.error('Erreur:', error);
                alert('Erreur lors de la mise à jour du statut');
            }
        });
    }
});