import os
import django
import sys
from django.core.management import call_command

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectmanager.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import CentreDI, GMR, Projet

def reset_db():
    """Supprime toutes les données existantes"""
    print("Nettoyage de la base de données...")
    Projet.objects.all().delete()
    GMR.objects.all().delete()
    CentreDI.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()

def create_test_data():
    try:
        reset_db()
        
        # Création des utilisateurs
        print("\nCréation des utilisateurs...")
        manager1 = User.objects.create_user(
            username='manager1',
            password='Manager1@2024',
            first_name='Jean',
            last_name='Dupont',
            email='jean.dupont@example.com'
        )
        manager1.is_staff = True
        manager1.save()
        print(f"Utilisateur créé: {manager1.username}")

        manager2 = User.objects.create_user(
            username='manager2',
            password='Manager2@2024',
            first_name='Marie',
            last_name='Martin',
            email='marie.martin@example.com'
        )
        manager2.is_staff = True
        manager2.save()
        print(f"Utilisateur créé: {manager2.username}")

        # Création des Centres DI
        print("\nCréation des Centres DI...")
        centres = {}
        for nom in ['Marseille', 'Nantes', 'Lyon', 'Paris', 'Lille']:
            centre = CentreDI.objects.create(nom=nom)
            centres[nom] = centre
            print(f"Centre DI créé: {centre.nom}")

        # Création des GMR
        print("\nCréation des GMR...")
        gmrs = {}
        gmr_data = [
            ('LARO', 'Languedoc Roussillon'),
            ('PAS', 'Provence Alpes Sud'),
            ('CAZ', 'Cévennes Auvergne'),
        ]
        for code, nom in gmr_data:
            gmr = GMR.objects.create(code=code, nom=nom)
            gmrs[code] = gmr
            print(f"GMR créé: {gmr.code} - {gmr.nom}")

        # Création des Projets
        print("\nCréation des Projets...")
        projets_data = [
            {
                'nom': 'Reconstruction Poste Source Marseille Nord',
                'centre_di': centres['Marseille'],
                'gmr': gmrs['PAS'],
                'manager': manager1,
                'selectionne': True
            },
            {
                'nom': 'Modernisation Réseau HTA Nantes Est',
                'centre_di': centres['Nantes'],
                'gmr': gmrs['LARO'],
                'manager': manager2,
                'selectionne': False
            },
            {
                'nom': 'Déploiement Smart Grid Lyon Centre',
                'centre_di': centres['Lyon'],
                'gmr': gmrs['CAZ'],
                'manager': manager1,
                'selectionne': True
            }
        ]

        for data in projets_data:
            projet = Projet.objects.create(**data)
            print(f"Projet créé: {projet.nom}")

        print("\nCréation des données de test terminée avec succès!")
        print("\nCompte de test:")
        print("manager1 / Manager1@2024")
        print("manager2 / Manager2@2024")

    except Exception as e:
        print(f"\nErreur lors de la création des données: {str(e)}")
        raise

if __name__ == '__main__':
    create_test_data()