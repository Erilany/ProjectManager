from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string, get_template
from django.template import TemplateDoesNotExist
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.db import transaction
from django.contrib.auth import logout
from .models import (
    Projet, RoleType, GroupeInterlocuteurs, Interlocuteur, 
    CentreDI, GMR, ProcessusEtape, ProcessusSelection, Action, Subtask
)
from django.core.exceptions import ObjectDoesNotExist
import logging
from django.views.decorators.csrf import ensure_csrf_cookie
from datetime import datetime, timedelta
from django.db.models import Q, Min, Max
import calendar

logger = logging.getLogger(__name__)

def login_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    projets = Projet.objects.all().select_related('centre_di', 'gmr', 'manager')
    projets_selectionnes = projets.filter(selectionne=True).order_by('nom')
    
    return render(request, 'dashboard.html', {
        'projets': projets,
        'projets_selectionnes': projets_selectionnes
    })

@login_required
def summary(request):
    projet_actif_id = request.session.get('projet_actif_id')
    if not projet_actif_id:
        return render(request, 'summary.html', {
            'etapes': [],
            'projet_actif': None
        })
    
    projet_actif = get_object_or_404(Projet, id=projet_actif_id)
    
    # Récupérer toutes les étapes avec leurs sélections pour ce projet
    etapes = ProcessusEtape.objects.all().prefetch_related('actions')
    
    # Récupérer les sélections existantes
    selections = ProcessusSelection.objects.filter(
        projet_id=projet_actif_id
    ).values_list('etape_id', 'selected')
    
    # Créer un dictionnaire des sélections
    selections_dict = dict(selections)
    
    # Ajouter l'information de sélection à chaque étape
    for etape in etapes:
        etape.est_selectionnee = selections_dict.get(etape.id, False)
    
    return render(request, 'summary.html', {
        'etapes': etapes,
        'projet_actif': projet_actif
    })

@login_required
def summary_content(request):
    projet_actif_id = request.session.get('projet_actif_id')
    context = {}
    
    if projet_actif_id:
        projet = get_object_or_404(Projet, id=projet_actif_id)
        etapes = ProcessusEtape.objects.all().order_by('ordre_global')
        
        # Récupérer les sélections pour ce projet
        selections = ProcessusSelection.objects.filter(projet=projet)
        etapes_selectionnees = {s.etape_id: s.selected for s in selections}
        
        # Marquer les étapes sélectionnées
        for etape in etapes:
            etape.est_selectionnee = etapes_selectionnees.get(etape.id, False)
        
        context = {
            'projet_actif': projet,
            'etapes': etapes,
        }
    
    html_content = render_to_string('partials/summary_content.html', context, request=request)
    return JsonResponse({
        'html': html_content,
        'projet_nom': context.get('projet_actif').nom if context.get('projet_actif') else None
    })

@login_required
def organization(request):
    projet_id = request.session.get('projet_actif_id')
    
    if not projet_id:
        return render(request, 'organization.html', {
            'roles_di': [],
            'interlocuteurs_di': [],
            'groupes': [],
            'projet_actif': None
        })
    
    # Récupérer le projet actif
    projet_actif = get_object_or_404(Projet, id=projet_id)
    
    # Récupérer les rôles DI (non filtrés car ils sont globaux)
    roles_di = RoleType.objects.filter(is_di=True)
    
    # Filtrer les interlocuteurs par projet
    interlocuteurs_di = Interlocuteur.objects.filter(
        role__is_di=True,
        projet_id=projet_id
    ).distinct()
    
    # Filtrer les groupes par projet
    groupes = GroupeInterlocuteurs.objects.filter(
        projet_id=projet_id
    ).distinct()
    
    return render(request, 'organization.html', {
        'roles_di': roles_di,
        'interlocuteurs_di': interlocuteurs_di,
        'groupes': groupes,
        'projet_actif': projet_actif
    })

@login_required
def process(request):
    if request.method == 'POST':
        # Return 405 Method Not Allowed if Accept header is not application/json
        if request.headers.get('Accept') != 'application/json':
            return JsonResponse({
                'status': 'error',
                'message': 'Cette URL n\'accepte que les requêtes JSON'
            }, status=405)
        return save_subtask(request)
    return render(request, 'process.html')

@login_required
def process_content(request):
    projet_actif_id = request.session.get('projet_actif_id')
    context = {}
    
    if projet_actif_id:
        projet = get_object_or_404(Projet, id=projet_actif_id)
        # Récupérer les étapes sélectionnées pour ce projet
        selections = ProcessusSelection.objects.filter(
            projet=projet,
            selected=True
        ).select_related('etape')
        
        # Récupérer toutes les actions associées à ces étapes pour ce projet
        actions = Action.objects.filter(
            etape__processusselection__projet=projet,
            etape__processusselection__selected=True
        ).select_related('etape').prefetch_related('subtasks')
        
        context = {
            'projet_actif': projet,
            'selections': selections,
            'actions': actions,
        }
    
    html_content = render_to_string('partials/process_content.html', context, request=request)
    return JsonResponse({
        'html': html_content,
        'projet_nom': context.get('projet_actif').nom if context.get('projet_actif') else None
    })

@login_required
def planning(request):
    projet_id = request.session.get('projet_actif_id')
    
    if not projet_id:
        return render(request, 'planning.html', {'weeks': [], 'subtasks': []})
    
    # Récupérer toutes les sous-tâches avec for_planning=True
    subtasks = Subtask.objects.filter(
        projet_id=projet_id,
        for_planning=True
    ).select_related('action')
    
    print(f"[DEBUG] Sous-tâches trouvées pour le planning:")
    for task in subtasks:
        print(f"[DEBUG] - ID: {task.id}, Sujet: {task.subject}, Privé: {task.is_private}, Dates: {task.start_date} - {task.end_date}")
    
    # Calculer les dates pour l'affichage
    today = datetime.today().date()
    start_date = today - timedelta(days=today.weekday())  # Commence au lundi de la semaine courante
    end_date = today + timedelta(days=365)  # Affiche toujours un an
    
    # Générer les semaines
    weeks = []
    current_date = start_date
    while current_date <= end_date:
        week_start = current_date
        weeks.append({
            'week_num': week_start.isocalendar()[1],
            'days': [week_start + timedelta(days=x) for x in range(5)]  # Lundi à vendredi
        })
        current_date += timedelta(days=7)
    
    context = {
        'weeks': weeks,
        'subtasks': subtasks,
        'today': today
    }
    
    return render(request, 'planning.html', context)

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
@require_POST
def toggle_projet_selection(request):
    try:
        # Essayer d'abord de récupérer depuis POST
        projet_id = request.POST.get('projet_id')
        
        # Si pas dans POST, essayer le corps JSON
        if not projet_id and request.content_type == 'application/json':
            data = json.loads(request.body)
            projet_id = data.get('projet_id')
            
        if not projet_id:
            return JsonResponse({
                'status': 'error',
                'message': 'projet_id manquant'
            }, status=400)
            
        projet = get_object_or_404(Projet, id=projet_id)
        projet.selectionne = not projet.selectionne
        projet.save()
        
        # Retourner aussi le HTML mis à jour
        projets_selectionnes = Projet.objects.filter(selectionne=True).select_related('centre_di', 'gmr')
        html = render_to_string(
            'partials/projets_selectionnes.html',
            {'projets_selectionnes': projets_selectionnes},
            request=request
        )
        
        logger.info(f"Toggle projet {projet_id}: selectionné = {projet.selectionne}")
        logger.info(f"Projets sélectionnés: {list(projets_selectionnes.values_list('id', flat=True))}")
        
        return JsonResponse({
            'status': 'success',
            'selectionne': projet.selectionne,
            'html': html
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Format JSON invalide'
        }, status=400)
    except Exception as e:
        logger.error(f"Erreur lors du toggle projet: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
@require_POST
def set_projet_actif(request):
    try:
        data = json.loads(request.body)
        projet_id = data.get('projet_id')
        
        # Vérifier si le projet existe et est sélectionné
        projet = get_object_or_404(Projet, id=projet_id, selectionne=True)
        
        # Mettre à jour la session uniquement si nécessaire
        if request.session.get('projet_actif_id') != projet.id:
            request.session['projet_actif_id'] = projet.id
            request.session.modified = True
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
@require_POST
def toggle_etape(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)
    
    try:
        data = json.loads(request.body)
        etape_id = data.get('etape_id')
        selected = data.get('selected', False)
        projet_actif_id = request.session.get('projet_actif_id')
        
        if not projet_actif_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Aucun projet actif'
            }, status=400)
            
        projet = get_object_or_404(Projet, id=projet_actif_id)
        etape = get_object_or_404(ProcessusEtape, id=etape_id)
        
        # Mettre à jour ou créer la sélection
        selection, created = ProcessusSelection.objects.update_or_create(
            projet=projet,
            etape=etape,
            defaults={'selected': selected}
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Sélection mise à jour'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Données JSON invalides'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def get_selected_projects(request):
    try:
        projets = Projet.objects.filter(selectionne=True)
        projet_actif_id = request.session.get('projet_actif_id')
        
        print(f"Projets sélectionnés: {list(projets.values('id', 'nom'))}")
        
        return JsonResponse({
            'status': 'success',
            'projets': list(projets.values('id', 'nom')),
            'projet_actif': projet_actif_id
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def get_selected_projects_content(request):
    try:
        projets_selectionnes = Projet.objects.filter(selectionne=True).select_related(
            'centre_di', 
            'gmr', 
            'manager'
        )
        html = render_to_string(
            'partials/projets_selectionnes.html',
            {'projets_selectionnes': projets_selectionnes},
            request=request
        )
        logger.info(f"Nombre de projets sélectionnés: {projets_selectionnes.count()}")
        return JsonResponse({
            'status': 'success',
            'html': html
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des projets sélectionnés: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def get_organization_content(request):
    try:
        projet_actif = get_object_or_404(Projet, id=request.session.get('projet_actif_id'))
        
        # Récupérer les données nécessaires
        roles_di = RoleType.objects.filter(is_di=True)
        roles_presta = RoleType.objects.filter(is_di=False)
        interlocuteurs_di = Interlocuteur.objects.filter(projet=projet_actif, role__is_di=True)
        interlocuteurs_presta = Interlocuteur.objects.filter(projet=projet_actif, role__is_di=False)
        groupes = GroupeInterlocuteurs.objects.filter(projet=projet_actif)
        
        # Rendre le HTML partiel
        html = render_to_string('partials/organization_content.html', {
            'projet_actif': projet_actif,
            'roles_di': roles_di,
            'roles_presta': roles_presta,
            'interlocuteurs_di': interlocuteurs_di,
            'interlocuteurs_presta': interlocuteurs_presta,
            'groupes': groupes,
        }, request=request)
        
        return JsonResponse({
            'status': 'success',
            'html': html,
            'projet_nom': projet_actif.nom
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du contenu de l'organisation: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
@require_POST
def update_status(request):
    try:
        data = json.loads(request.body)
        type_obj = data.get('type')
        obj_id = data.get('id')
        new_status = data.get('status')
        
        if type_obj == 'etape':
            obj = ProcessusEtape.objects.get(id=obj_id)
        else:
            obj = Action.objects.get(id=obj_id)
            
        obj.status = new_status
        obj.save()
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@login_required
def get_subtask(request, subtask_id):
    try:
        subtask = Subtask.objects.get(id=subtask_id)
        return JsonResponse({
            'status': 'success',
            'subtask': {
                'subject': subtask.subject,
                'comments': subtask.comments,
                'start_date': subtask.start_date.isoformat() if subtask.start_date else None,
                'end_date': subtask.end_date.isoformat() if subtask.end_date else None,
                'status': subtask.status,
                'is_private': subtask.is_private
            }
        })
    except Subtask.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Sous-tâche non trouvée'
        }, status=404)

@login_required
@require_POST
def delete_subtask(request, subtask_id):
    try:
        subtask = Subtask.objects.get(id=subtask_id)
        subtask.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Sous-tâche supprimée avec succès'
        })
    except Subtask.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Sous-tâche non trouvée'
        }, status=404)

@login_required
@require_POST
def update_subtask(request, subtask_id):
    try:
        data = json.loads(request.body)
        subtask = Subtask.objects.get(id=subtask_id)
        
        if subtask.created_by != request.user and not request.user.is_staff:
            return JsonResponse({
                'status': 'error',
                'message': 'Vous n\'avez pas les droits pour modifier cette sous-tâche'
            }, status=403)
        
        subtask.subject = data['subject']
        subtask.comments = data.get('comments', '')
        subtask.start_date = data.get('start_date')
        subtask.end_date = data.get('end_date')
        subtask.status = data.get('status', 'todo')
        subtask.is_private = data.get('is_private', False)
        subtask.for_planning = data.get('for_planning', False)
        
        subtask.save()
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
@require_POST
def save_interlocuteur(request):
    try:
        data = request.POST
        projet_id = request.session.get('projet_actif_id')
        
        if not projet_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Aucun projet actif sélectionné'
            })

        # Créer ou mettre à jour l'interlocuteur
        interlocuteur_data = {
            'prenom': data.get('prenom'),
            'nom': data.get('nom'),
            'email': data.get('email', ''),
            'telephone': data.get('telephone', ''),
            'projet_id': projet_id
        }

        # Gérer le rôle
        role_id = data.get('role_id')
        if role_id:
            role = get_object_or_404(RoleType, id=role_id)
            interlocuteur_data['role'] = role
        else:
            # Créer un nouveau rôle si nécessaire
            role_nom = data.get('role_nom')
            if role_nom:
                role = RoleType.objects.create(
                    nom=role_nom,
                    is_di=data.get('is_di') == 'true'
                )
                interlocuteur_data['role'] = role

        # Gérer le groupe si présent
        groupe_id = data.get('groupe_id')
        if groupe_id:
            groupe = get_object_or_404(GroupeInterlocuteurs, id=groupe_id)
            interlocuteur_data['groupe'] = groupe

        # Créer l'interlocuteur
        Interlocuteur.objects.create(**interlocuteur_data)

        return JsonResponse({
            'status': 'success',
            'message': 'Interlocuteur enregistré avec succès'
        })

    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de l'interlocuteur: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
@require_POST
def save_groupe(request):
    try:
        data = request.POST
        projet_id = request.session.get('projet_actif_id')
        
        if not projet_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Aucun projet actif sélectionné'
            })

        # Créer le groupe
        groupe = GroupeInterlocuteurs.objects.create(
            nom=data.get('nom'),
            projet_id=projet_id
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Groupe créé avec succès',
            'groupe': {
                'id': groupe.id,
                'nom': groupe.nom
            }
        })

    except Exception as e:
        logger.error(f"Erreur lors de la création du groupe: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
@require_POST
def delete_groupe(request, groupe_id):
    try:
        groupe = get_object_or_404(GroupeInterlocuteurs, id=groupe_id)
        # Vérifier que le groupe appartient au projet actif
        if str(groupe.projet_id) != str(request.session.get('projet_actif_id')):
            raise PermissionError("Vous n'avez pas la permission de supprimer ce groupe")
        
        groupe.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Groupe supprimé avec succès'
        })
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du groupe: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def get_groupe(request, groupe_id):
    try:
        groupe = get_object_or_404(GroupeInterlocuteurs, id=groupe_id)
        # Vérifier que le groupe appartient au projet actif
        if str(groupe.projet_id) != str(request.session.get('projet_actif_id')):
            raise PermissionError("Vous n'avez pas la permission de voir ce groupe")
        
        return JsonResponse({
            'status': 'success',
            'groupe': {
                'id': groupe.id,
                'nom': groupe.nom
            }
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du groupe: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
@require_POST
def update_groupe(request, groupe_id):
    try:
        groupe = get_object_or_404(GroupeInterlocuteurs, id=groupe_id)
        # Vérifier que le groupe appartient au projet actif
        if str(groupe.projet_id) != str(request.session.get('projet_actif_id')):
            raise PermissionError("Vous n'avez pas la permission de modifier ce groupe")
        
        # Récupérer les données soit de POST soit du corps de la requête
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
            
        groupe.nom = data.get('nom')
        groupe.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Groupe mis à jour avec succès',
            'groupe': {
                'id': groupe.id,
                'nom': groupe.nom
            }
        })
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du groupe: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def organization_content(request):
    try:
        projet_actif = get_object_or_404(Projet, id=request.session.get('projet_actif_id'))
        if not projet_actif:
            return HttpResponse('<div class="alert alert-info">Veuillez sélectionner un projet pour voir son organisation.</div>')

        # Récupérer les données nécessaires pour la page organization
        roles_di = RoleType.objects.filter(is_di=True).order_by('nom')
        interlocuteurs_di = Interlocuteur.objects.filter(
            projet=projet_actif,
            role__is_di=True
        ).select_related('role').order_by('role__nom', 'nom')

        groupes = GroupeInterlocuteurs.objects.filter(projet=projet_actif).order_by('nom')
        interlocuteurs_non_di = Interlocuteur.objects.filter(
            projet=projet_actif,
            role__is_di=False
        ).select_related('role', 'groupe').order_by('groupe__nom', 'nom')

        # Ajouter des logs pour le débogage
        logger.debug(f"Projet actif: {projet_actif.nom}")
        logger.debug(f"Nombre de rôles DI: {roles_di.count()}")
        logger.debug(f"Nombre d'interlocuteurs DI: {interlocuteurs_di.count()}")
        logger.debug(f"Nombre de groupes: {groupes.count()}")
        logger.debug(f"Nombre d'interlocuteurs non DI: {interlocuteurs_non_di.count()}")

        context = {
            'projet_actif': projet_actif,
            'roles_di': roles_di,
            'interlocuteurs_di': interlocuteurs_di,
            'groupes': groupes,
            'interlocuteurs_non_di': interlocuteurs_non_di,
        }

        # Rendre uniquement le contenu de la page organization
        return render(request, 'partials/organization_content.html', context)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du contenu: {str(e)}")
        return HttpResponse(
            '<div class="alert alert-danger">Une erreur est survenue lors de la mise à jour du contenu.</div>',
            status=500
        )

def projet_context(request):
    """
    Context processor pour rendre les projets disponibles globalement.
    """
    # Log pour suivre les appels
    print("[DEBUG] Appel du context processor projet_context")
    
    # Ne pas exécuter pour les requêtes AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {}
    
    try:
        projets = Projet.objects.filter(selectionne=True)
        projet_actif_id = request.session.get('projet_actif_id')
        
        if projet_actif_id:
            projet_actif = projets.filter(id=projet_actif_id).first()
            if not projet_actif and projets.exists():
                projet_actif = projets.first()
                request.session['projet_actif_id'] = projet_actif.id
        elif projets.exists():
            projet_actif = projets.first()
            request.session['projet_actif_id'] = projet_actif.id
        else:
            projet_actif = None

        return {
            'projets': projets,
            'projet_actif': projet_actif
        }
    except Exception as e:
        print(f"Erreur dans projet_context: {e}")
        return {}

@login_required
def save_subtask(request):
    if request.method == 'POST':
        try:
            data = request.POST
            
            # Récupérer l'action parent
            action_id = data.get('action_id')
            if not action_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Action ID manquant'
                }, status=400)
                
            action = Action.objects.get(id=action_id)
            
            # Récupérer l'ID de la sous-tâche si c'est une modification
            subtask_id = data.get('subtask_id')
            if subtask_id:
                subtask = Subtask.objects.get(id=subtask_id)
            else:
                subtask = Subtask(
                    action=action,
                    projet=action.projet,
                    created_by=request.user
                )
            
            # Mettre à jour les champs
            subtask.subject = data.get('subject')
            subtask.comments = data.get('comments', '')
            subtask.status = data.get('status', 'todo')
            subtask.is_private = data.get('is_private') == 'true'
            subtask.in_planning = data.get('in_planning') == 'true'
            
            # Gérer les dates
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            
            if start_date:
                subtask.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if end_date:
                subtask.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            subtask.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Sous-tâche enregistrée avec succès',
                'subtask_id': subtask.id
            })
            
        except Action.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Action non trouvée'
            }, status=404)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Méthode non autorisée'
    }, status=405)

@login_required
def update_subtask_status(request):
    if request.method == 'POST':
        try:
            subtask_id = request.POST.get('subtask_id')
            new_status = request.POST.get('status')
            
            subtask = Subtask.objects.get(id=subtask_id)
            subtask.status = new_status
            subtask.save()
            
            # Mettre à jour le statut de l'action parent
            update_action_status(subtask.action)
            
            return JsonResponse({
                'status': 'success',
                'status_display': subtask.get_status_display(),
                'action_status': subtask.action.status,
                'action_status_display': subtask.action.get_status_display()
            })
            
        except Subtask.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Sous-tâche non trouvée'
            }, status=404)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Méthode non autorisée'
    }, status=405)

def update_action_status(action):
    """Met à jour le statut d'une action en fonction de ses sous-tâches"""
    subtasks = action.subtasks.all()
    
    if not subtasks.exists():
        return
    
    # Compter les statuts des sous-tâches
    status_counts = {
        'todo': subtasks.filter(status='todo').count(),
        'in_progress': subtasks.filter(status='in_progress').count(),
        'waiting': subtasks.filter(status='waiting').count(),
        'done': subtasks.filter(status='done').count()
    }
    
    total = sum(status_counts.values())
    
    # Déterminer le nouveau statut
    if status_counts['done'] == total:
        new_status = 'done'
    elif status_counts['todo'] == total:
        new_status = 'todo'
    elif status_counts['waiting'] > 0:
        new_status = 'waiting'
    else:
        new_status = 'in_progress'
    
    # Mettre à jour le statut de l'action
    action.status = new_status
    action.save()

# Retourne le HTML des sous-tâches pour une action donnée
def get_subtasks(request, action_id):
    try:
        logger.info(f"=== Début get_subtasks pour action_id: {action_id} ===")
        action = get_object_or_404(Action, id=action_id)
        logger.info(f"Action trouvée: {action}")
        
        subtasks = action.subtasks.all()
        logger.info(f"Sous-tâches trouvées: {list(subtasks)}")
        
        html = render_to_string('partials/subtasks.html', {
            'action': action,
            'subtasks': subtasks,
        })
        logger.info("HTML des sous-tâches généré avec succès")
        
        return JsonResponse({
            'status': 'success',
            'html': html
        })
    except Exception as e:
        logger.error(f"Erreur dans get_subtasks: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)