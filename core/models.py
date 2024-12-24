from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import datetime

class CentreDI(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Centre DI"
        verbose_name_plural = "Centres DI"
        ordering = ['nom']

class GMR(models.Model):
    code = models.CharField(max_length=10)
    nom = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.nom}"

    class Meta:
        verbose_name = "GMR"
        verbose_name_plural = "GMR"
        ordering = ['code']

class Projet(models.Model):
    nom = models.CharField(max_length=200)
    centre_di = models.ForeignKey(CentreDI, on_delete=models.SET_NULL, null=True, verbose_name="Centre DI")
    gmr = models.ForeignKey(GMR, on_delete=models.SET_NULL, null=True, verbose_name="GMR")
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    selectionne = models.BooleanField(default=False)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ['-date_creation']

class RoleType(models.Model):
    nom = models.CharField(max_length=100)
    is_di = models.BooleanField(default=False, verbose_name="Est un rôle DI")
    ordre = models.IntegerField(default=0)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = "Type de rôle"
        verbose_name_plural = "Types de rôles"

    def __str__(self):
        return self.nom

class GroupeInterlocuteurs(models.Model):
    nom = models.CharField(max_length=100)
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='groupes_interlocuteurs')
    ordre = models.IntegerField(default=0)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = "Groupe d'interlocuteurs"
        verbose_name_plural = "Groupes d'interlocuteurs"

    def __str__(self):
        return f"{self.projet.nom} - {self.nom}"

class Interlocuteur(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='interlocuteurs')
    groupe = models.ForeignKey(GroupeInterlocuteurs, on_delete=models.CASCADE, related_name='interlocuteurs', null=True, blank=True)
    role = models.ForeignKey(RoleType, on_delete=models.PROTECT, related_name='interlocuteurs')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    commentaire = models.TextField(blank=True)

    class Meta:
        ordering = ['groupe__ordre', 'role__ordre', 'nom']
        verbose_name = "Interlocuteur"
        verbose_name_plural = "Interlocuteurs"

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.role}"

class ProcessusEtape(models.Model):
    STATUS_CHOICES = [
        ('todo', 'À faire'),
        ('in-progress', 'En cours'),
        ('waiting', 'En attente'),
        ('done', 'Terminé'),
    ]

    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    ordre_global = models.IntegerField(default=0)
    ordre = models.IntegerField(default=0)
    actif = models.BooleanField(default=True)
    selectionne = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo',
        verbose_name="Statut"
    )

    class Meta:
        ordering = ['ordre_global', 'nom']
        verbose_name = "Étape du processus"
        verbose_name_plural = "Étapes du processus"

    def __str__(self):
        return f"{self.ordre_global} - {self.nom}"

    def get_status_display_color(self):
        """Retourne la couleur associée au statut"""
        status_colors = {
            'todo': 'secondary',     # Gris
            'in-progress': 'primary', # Bleu
            'waiting': 'warning',     # Jaune
            'done': 'success'         # Vert
        }
        return status_colors.get(self.status, 'secondary')

class ProcessusSelection(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE)
    etape = models.ForeignKey(ProcessusEtape, on_delete=models.CASCADE)
    selected = models.BooleanField(default=False)
    date_selection = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['projet', 'etape']
        
    def __str__(self):
        return f"{self.projet.nom} - {self.etape.nom} ({'sélectionné' if self.selected else 'non sélectionné'})"

class Action(models.Model):
    STATUS_CHOICES = [
        ('todo', 'À faire'),
        ('in-progress', 'En cours'),
        ('waiting', 'En attente'),
        ('done', 'Terminé'),
    ]

    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    delai = models.CharField(max_length=100, blank=True)
    ordre = models.IntegerField()
    etape = models.ForeignKey(ProcessusEtape, on_delete=models.CASCADE, related_name='actions')
    projet = models.ForeignKey('Projet', on_delete=models.CASCADE, related_name='actions', null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo',
        verbose_name="Statut"
    )

    class Meta:
        ordering = ['ordre', 'titre']
        verbose_name = "Action"
        verbose_name_plural = "Actions"

    def __str__(self):
        return f"{self.ordre} - {self.titre}"
    
    def get_status_display_color(self):
        """Retourne la couleur associée au statut"""
        status_colors = {
            'todo': 'secondary',     # Gris
            'in-progress': 'primary', # Bleu
            'waiting': 'warning',     # Jaune
            'done': 'success'         # Vert
        }
        return status_colors.get(self.status, 'secondary')
    
class Subtask(models.Model):
    STATUS_CHOICES = [
        ('todo', 'À faire'),
        ('in-progress', 'En cours'),
        ('waiting', 'En attente'),
        ('done', 'Terminé')
    ]
    
    action = models.ForeignKey(Action, on_delete=models.CASCADE, related_name='subtasks')
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    comments = models.TextField(blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    is_private = models.BooleanField(default=False)
    in_planning = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Sous-tâche"
        verbose_name_plural = "Sous-tâches"
        db_table = 'core_subtask'

    def __str__(self):
        return f"{self.subject} ({self.get_status_display()})"

    def get_status_display_color(self):
        """Retourne la couleur associée au statut"""
        status_colors = {
            'todo': 'secondary',     # Gris
            'in-progress': 'primary', # Bleu
            'waiting': 'warning',     # Jaune
            'done': 'success'         # Vert
        }
        return status_colors.get(self.status, 'secondary')

# Ajoutez les autres modèles (ProcessusEtape, Action, Subtask, etc.) class Subtask(models.Model):
    # ... autres champs ...
    is_private = models.BooleanField(default=False)
    in_planning = models.BooleanField(default=False)