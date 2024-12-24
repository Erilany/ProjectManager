from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_redirect, name='login_redirect'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('summary/', views.summary, name='summary'),
    path('organization/', views.organization, name='organization'),
    path('process/', views.process, name='process'),
    path('planning/', views.planning, name='planning'),
    path('profile/', views.profile, name='profile'),
    
    # API endpoints
    path('toggle-projet-selection/', views.toggle_projet_selection, name='toggle_projet_selection'),
    path('set-projet-actif/', views.set_projet_actif, name='set_projet_actif'),
    path('toggle-etape/', views.toggle_etape, name='toggle_etape'),
    path('get-selected-projects/', views.get_selected_projects, name='get_selected_projects'),
    path('get-selected-projects-content/', views.get_selected_projects_content, name='get_selected_projects_content'),
    path('organization/content/', views.get_organization_content, name='get_organization_content'),
    
    path('summary/content/', views.summary_content, name='summary_content'),
    path('summary/toggle_etape/', views.toggle_etape, name='toggle_etape'),

    path('process/content/', views.process_content, name='process_content'),
    path('process/save_subtask/', views.save_subtask, name='save_subtask'),
    path('process/update_subtask_status/', views.update_subtask_status, name='update_subtask_status'),
    path('process/get_subtasks/<int:action_id>/', views.get_subtasks, name='get_subtasks'),

    # Interlocuteurs et groupes
    path('save-interlocuteur/', views.save_interlocuteur, name='save_interlocuteur'),
    path('save-groupe/', views.save_groupe, name='save_groupe'),
    path('delete-groupe/<int:groupe_id>/', views.delete_groupe, name='delete_groupe'),
    path('get-groupe/<int:groupe_id>/', views.get_groupe, name='get_groupe'),
    path('update-groupe/<int:groupe_id>/', views.update_groupe, name='update_groupe'),
    path('process/content/', views.process_content, name='process_content'),
]