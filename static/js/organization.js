class OrganizationManager {
    constructor() {
        this.initEventListeners();
        this.initModals();
        this.initDataTables();
        this.initProjectSelector();
        
        // Charger le contenu initial
        this.loadOrganizationContent();
        
        console.log('OrganizationManager initialized');
    }

    // Nouvelle méthode pour charger le contenu
    loadOrganizationContent() {
        fetch('/organization/content/')
            .then(response => response.json())
            .then(contentData => {
                if (contentData.html) {
                    const container = document.querySelector('#organization-content');
                    if (container) {
                        container.innerHTML = contentData.html;
                        this.initDataTables();
                        this.initEventListeners();
                    }
                    
                    // Mettre à jour le titre si nécessaire
                    if (contentData.projet_nom) {
                        const titleElement = document.querySelector('.container-fluid h1.h3');
                        if (titleElement) {
                            titleElement.textContent = `Organisation - ${contentData.projet_nom}`;
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Erreur lors du chargement initial:', error);
                this.showError('Erreur lors du chargement de la page');
            });
    }

    initDataTables() {
        // Configuration française de DataTables
        const frenchTranslation = {
            "emptyTable": "Aucune donnée disponible",
            "info": "Affichage de _START_ à _END_ sur _TOTAL_ entrées",
            "infoEmpty": "Affichage de 0 à 0 sur 0 entrée",
            "infoFiltered": "(filtré sur _MAX_ entrées au total)",
            "lengthMenu": "Afficher _MENU_ entrées",
            "loadingRecords": "Chargement...",
            "processing": "Traitement...",
            "search": "Rechercher :",
            "zeroRecords": "Aucun résultat trouvé",
            "paginate": {
                "first": "Premier",
                "last": "Dernier",
                "next": "Suivant",
                "previous": "Précédent"
            }
        };

        // Initialiser les DataTables si elles existent
        const tables = document.querySelectorAll('.datatable');
        tables.forEach(table => {
            $(table).DataTable({
                language: frenchTranslation,
                order: [[0, 'asc']],
                pageLength: 10,
                responsive: true
            });
        });
    }

    initModals() {
        // Initialiser les modales Bootstrap
        const interlocuteurModalEl = document.getElementById('interlocuteurModal');
        const groupeModalEl = document.getElementById('groupeModal');
        
        if (interlocuteurModalEl) {
            this.interlocuteurModal = new bootstrap.Modal(interlocuteurModalEl);
        }
        if (groupeModalEl) {
            this.groupeModal = new bootstrap.Modal(groupeModalEl);
        }
    }

    initEventListeners() {
        // Boutons d'ajout d'interlocuteur
        document.querySelectorAll('.add-interlocuteur').forEach(button => {
            button.addEventListener('click', (e) => this.handleAddInterlocuteur(e));
        });

        // Boutons d'édition d'interlocuteur
        document.querySelectorAll('.edit-interlocuteur').forEach(button => {
            button.addEventListener('click', (e) => this.handleEditInterlocuteur(e));
        });

        // Boutons de suppression d'interlocuteur
        document.querySelectorAll('.delete-interlocuteur').forEach(button => {
            button.addEventListener('click', (e) => this.handleDeleteInterlocuteur(e));
        });

        // Bouton d'ajout de groupe
        const addGroupeBtn = document.getElementById('add-groupe');
        if (addGroupeBtn) {
            addGroupeBtn.addEventListener('click', () => this.handleAddGroupe());
        }

        // Boutons d'édition de groupe
        document.querySelectorAll('.edit-groupe').forEach(button => {
            button.addEventListener('click', (e) => this.handleEditGroupe(e));
        });

        // Boutons de suppression de groupe
        document.querySelectorAll('.delete-groupe').forEach(button => {
            button.addEventListener('click', (e) => this.handleDeleteGroupe(e));
        });

        // Bouton de sauvegarde d'interlocuteur
        const saveInterlocuteurBtn = document.getElementById('saveInterlocuteur');
        if (saveInterlocuteurBtn) {
            saveInterlocuteurBtn.addEventListener('click', () => this.saveInterlocuteur());
        }

        // Bouton de sauvegarde de groupe
        const saveGroupeBtn = document.getElementById('saveGroupe');
        if (saveGroupeBtn) {
            saveGroupeBtn.addEventListener('click', () => this.saveGroupe());
        }
    }

    initProjectSelector() {
        const selector = document.querySelector('.projet-selector');
        if (selector) {
            selector.addEventListener('change', async (event) => {
                const projetId = event.target.value;
                console.log('Changement de projet:', projetId);
                
                try {
                    // 1. Mettre à jour le projet actif
                    const response = await fetch('/set-projet-actif/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: JSON.stringify({ projet_id: projetId })
                    });

                    if (!response.ok) {
                        throw new Error(`Erreur HTTP: ${response.status}`);
                    }

                    const data = await response.json();
                    if (data.status === 'success') {
                        // 2. Recharger le contenu de la page
                        const contentResponse = await fetch('/organization/content/');
                        if (!contentResponse.ok) {
                            throw new Error('Erreur lors du chargement du contenu');
                        }
                        const contentData = await contentResponse.json();
                        
                        if (contentData.html) {
                            // Mettre à jour le contenu
                            const container = document.querySelector('#organization-content');
                            if (container) {
                                container.innerHTML = contentData.html;
                                // Réinitialiser les composants
                                this.initDataTables();
                                this.initModals();
                                this.initEventListeners();
                            }

                            // Mettre à jour le titre
                            const titleElement = document.querySelector('.container-fluid h1.h3');
                            if (titleElement && contentData.projet_nom) {
                                titleElement.textContent = `Organisation - ${contentData.projet_nom}`;
                            }
                        }
                    } else {
                        throw new Error(data.message || 'Erreur lors de la mise à jour');
                    }
                } catch (error) {
                    console.error('Erreur:', error);
                    this.showError('Erreur lors du changement de projet');
                }
            });
        }
    }

    handleAddGroupe() {
        const form = document.getElementById('groupeForm');
        if (form) {
            form.reset();
            // Réinitialiser l'ID du groupe pour une nouvelle création
            const groupeIdInput = form.querySelector('#groupe_id');
            if (groupeIdInput) {
                groupeIdInput.value = '';
            }
            // Mettre à jour le titre
            const modalTitle = document.querySelector('#groupeModal .modal-title');
            if (modalTitle) {
                modalTitle.textContent = 'Ajouter un groupe d\'interlocuteurs';
            }
        }
        if (this.groupeModal) {
            this.groupeModal.show();
        }
    }

    async handleEditGroupe(event) {
        event.preventDefault();
        const groupeId = event.currentTarget.closest('[data-groupe-id]').dataset.groupeId;
        try {
            const response = await fetch(`/get-groupe/${groupeId}/`);
            if (!response.ok) throw new Error('Erreur réseau');

            const data = await response.json();
            if (data.status === 'success') {
                this.populateGroupeForm(data.groupe);
                if (this.groupeModal) {
                    this.groupeModal.show();
                }
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            this.showError(`Erreur : ${error.message}`);
        }
    }

    async handleDeleteGroupe(event) {
        event.preventDefault();
        if (!confirm('Êtes-vous sûr de vouloir supprimer ce groupe ? Cette action supprimera également tous les interlocuteurs associés.')) {
            return;
        }

        const groupeId = event.currentTarget.closest('[data-groupe-id]').dataset.groupeId;
        try {
            const response = await fetch(`/delete-groupe/${groupeId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                }
            });

            if (!response.ok) throw new Error('Erreur réseau');

            const data = await response.json();
            if (data.status === 'success') {
                this.showSuccess('Groupe supprimé avec succès');
                window.location.reload();
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            this.showError(`Erreur : ${error.message}`);
        }
    }

    populateGroupeForm(groupe) {
        const form = document.getElementById('groupeForm');
        if (!form) return;

        const groupeIdInput = form.querySelector('#groupe_id');
        const nomInput = form.querySelector('#nom');
        
        if (groupeIdInput) groupeIdInput.value = groupe.id;
        if (nomInput) nomInput.value = groupe.nom;

        // Mettre à jour le titre
        const modalTitle = document.querySelector('#groupeModal .modal-title');
        if (modalTitle) {
            modalTitle.textContent = 'Modifier le groupe';
        }
    }

    handleAddInterlocuteur(event) {
        event.preventDefault();
        const button = event.currentTarget;
        const roleId = button.dataset.roleId;
        const groupeId = button.dataset.groupeId;
        const isDI = button.dataset.isDi === 'true';
        const roleName = button.dataset.roleName;
    
        // Réinitialiser le formulaire
        const form = document.getElementById('interlocuteurForm');
        if (form) {
            form.reset();
            
            // Définir les valeurs cachées
            const roleIdInput = form.querySelector('#role_id');
            const groupeIdInput = form.querySelector('#groupe_id');
            const isDiInput = form.querySelector('#is_di');
            
            if (roleIdInput) roleIdInput.value = roleId || '';
            if (groupeIdInput) groupeIdInput.value = groupeId || '';
            if (isDiInput) isDiInput.value = isDI;
            
            // Gérer l'affichage des champs selon le contexte
            const nonDiFields = form.querySelectorAll('.non-di-field');
            const diFields = form.querySelectorAll('.di-field');
        
            if (isDI) {
                nonDiFields.forEach(field => field.style.display = 'none');
                diFields.forEach(field => field.style.display = 'block');
            } else {
                nonDiFields.forEach(field => field.style.display = 'block');
                diFields.forEach(field => field.style.display = 'block');
            }
        
            // Si c'est un rôle DI, mettre à jour le titre et masquer le champ fonction
            const modalTitle = document.querySelector('#interlocuteurModal .modal-title');
            if (isDI && modalTitle) {
                modalTitle.textContent = `Ajouter ${roleName}`;
                const roleNomInput = form.querySelector('#role_nom');
                if (roleNomInput) {
                    roleNomInput.value = roleName;
                    roleNomInput.readOnly = true;
                }
            } else if (modalTitle) {
                modalTitle.textContent = 'Ajouter un interlocuteur';
                const roleNomInput = form.querySelector('#role_nom');
                if (roleNomInput) {
                    roleNomInput.value = '';
                    roleNomInput.readOnly = false;
                }
            }
        }
    
        // Afficher la modale
        if (this.interlocuteurModal) {
            this.interlocuteurModal.show();
        }
    }

    async handleEditInterlocuteur(event) {
        const interlocuteurId = event.currentTarget.closest('[data-interlocuteur-id]').dataset.interlocuteurId;
        try {
            const response = await fetch(`/organization/get-interlocuteur/${interlocuteurId}/`);
            if (!response.ok) throw new Error('Erreur réseau');

            const data = await response.json();
            if (data.status === 'success') {
                this.populateInterlocuteurForm(data.interlocuteur);
                if (this.interlocuteurModal) {
                    this.interlocuteurModal.show();
                }
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            this.showError(`Erreur : ${error.message}`);
        }
    }

    async handleDeleteInterlocuteur(event) {
        if (!confirm('Êtes-vous sûr de vouloir supprimer cet interlocuteur ?')) return;

        const interlocuteurId = event.currentTarget.closest('[data-interlocuteur-id]').dataset.interlocuteurId;
        try {
            const response = await fetch(`/organization/delete-interlocuteur/${interlocuteurId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                }
            });

            if (!response.ok) throw new Error('Erreur réseau');

            const data = await response.json();
            if (data.status === 'success') {
                this.showSuccess('Interlocuteur supprimé avec succès');
                window.location.reload();
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            this.showError(`Erreur : ${error.message}`);
        }
    }

    populateInterlocuteurForm(interlocuteur) {
        const form = document.getElementById('interlocuteurForm');
        if (!form) return;

        const fields = ['prenom', 'nom', 'email', 'telephone', 'role_id', 'groupe_id'];
        fields.forEach(field => {
            const input = form.querySelector(`#${field}`);
            if (input) {
                input.value = interlocuteur[field] || '';
            }
        });

        // Gérer l'affichage des champs selon le type d'interlocuteur
        const isDI = interlocuteur.role?.is_di || false;
        const nonDiFields = form.querySelectorAll('.non-di-field');
        const diFields = form.querySelectorAll('.di-field');

        if (isDI) {
            nonDiFields.forEach(field => field.style.display = 'none');
            diFields.forEach(field => field.style.display = 'block');
        } else {
            nonDiFields.forEach(field => field.style.display = 'block');
            diFields.forEach(field => field.style.display = 'block');
        }
    }

    saveInterlocuteur() {
        const form = document.getElementById('interlocuteurForm');
        if (!form) {
            console.error('Formulaire non trouvé');
            return;
        }

        // Vérifier que tous les champs requis sont remplis
        const prenom = form.querySelector('#prenom')?.value;
        const nom = form.querySelector('#nom')?.value;

        if (!prenom || !nom) {
            this.showError('Veuillez remplir tous les champs obligatoires');
            return;
        }

        const formData = new FormData(form);

        fetch('/save-interlocuteur/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                if (this.interlocuteurModal) {
                    this.interlocuteurModal.hide();
                }
                window.location.reload();
            } else {
                console.error('Erreur:', data.message);
                this.showError(data.message || 'Une erreur est survenue');
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            this.showError('Une erreur est survenue lors de la sauvegarde');
        });
    }

    saveGroupe() {
        const form = document.getElementById('groupeForm');
        if (!form) {
            console.error('Formulaire de groupe non trouvé');
            return;
        }

        const nomInput = form.querySelector('#nom');
        if (!nomInput?.value) {
            this.showError('Veuillez saisir un nom de groupe');
            return;
        }

        const formData = new FormData(form);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        if (!csrfToken) {
            console.error('Token CSRF non trouvé');
            this.showError('Erreur de sécurité : token CSRF manquant');
            return;
        }

        const groupeId = form.querySelector('#groupe_id')?.value;
        const url = groupeId ? `/update-groupe/${groupeId}/` : '/save-groupe/';

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(Object.fromEntries(formData))
        })
        .then(async response => {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || 'Une erreur est survenue');
            }
            return data;
        })
        .then(data => {
            if (data.status === 'success') {
                if (this.groupeModal) {
                    this.groupeModal.hide();
                }
                this.showSuccess(data.message || 'Groupe sauvegardé avec succès');
                
                // Attendre un peu avant de recharger le contenu
                setTimeout(() => {
                    fetch('/organization/content/')
                        .then(response => response.json())
                        .then(contentData => {
                            if (contentData.html) {
                                const container = document.querySelector('#organization-content');
                                if (container) {
                                    container.innerHTML = contentData.html;
                                    this.initDataTables();
                                    this.initEventListeners();
                                }
                            }
                        })
                        .catch(error => {
                            console.error('Erreur lors du rechargement:', error);
                            // En cas d'erreur de rechargement, on attend encore un peu avant de recharger la page
                            setTimeout(() => window.location.reload(), 500);
                        });
                }, 500); // Attendre 500ms avant de recharger
            } else {
                throw new Error(data.message || 'Une erreur est survenue');
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            this.showError(error.message || 'Une erreur est survenue lors de la sauvegarde');
        });
    }

    showError(message) {
        const alertsContainer = document.getElementById('alerts-container');
        if (alertsContainer) {
            const alert = document.createElement('div');
            alert.className = 'alert alert-danger alert-dismissible fade show';
            alert.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            alertsContainer.appendChild(alert);
        }
    }

    showSuccess(message) {
        const alertsContainer = document.getElementById('alerts-container');
        if (alertsContainer) {
            const alert = document.createElement('div');
            alert.className = 'alert alert-success alert-dismissible fade show';
            alert.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            alertsContainer.appendChild(alert);
        }
    }
}

// Initialisation quand le document est prêt
document.addEventListener('DOMContentLoaded', () => {
    window.organizationManager = new OrganizationManager();
});