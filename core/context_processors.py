from .models import Projet

def projet_context(request):
    """
    Context processor pour rendre les projets disponibles globalement.
    """
    try:
        # Récupérer uniquement les projets sélectionnés
        projets = Projet.objects.filter(selectionne=True)
        
        # Gérer le projet actif
        projet_actif_id = request.session.get('projet_actif_id')
        
        if projet_actif_id:
            projet_actif = projets.filter(id=projet_actif_id).first()
            if not projet_actif:
                projet_actif = projets.first()
                if projet_actif:
                    request.session['projet_actif_id'] = projet_actif.id
        else:
            projet_actif = projets.first()
            if projet_actif:
                request.session['projet_actif_id'] = projet_actif.id

        return {
            'projets': projets,
            'projet_actif': projet_actif
        }
    except Exception as e:
        # En cas d'erreur, retourner des valeurs par défaut
        return {
            'projets': [],
            'projet_actif': None
        }