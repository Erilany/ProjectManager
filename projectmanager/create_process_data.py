import os
import django
import csv
from django.db import transaction

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectmanager.settings')
django.setup()

from core.models import ProcessusEtape, Action

# Dictionnaire pour stocker les étapes uniques
ETAPES_DATA = [
    (1, "Mener les études décisionnelles"),
    (1, "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (2, "Mener les études d'ingénierie détaillées pour un projet LA/LS"),
    (2, "Mener la concertation et les procédures administratives"),
    (2, "Mener les études d'ingénierie détaillées pour un projet Poste/CC"),
    (3, "Réaliser les travaux"),
    (4, "Préparer et réaliser la MEC"),
    (5, "Clôturer le projet")
]

ACTIONS_DATA = [
    # (ordre, titre, description, delai, etape)
    (0, "Rédiger la décision d'abandon et créer une demande dans référencement et structuration", "-", "", "Clôturer le projet"),
    (1, "Réaliser la revue du CCF", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (1, "Obtenir la validation du fuseau/emplacement de moindre impact", "-", "", "Mener la concertation et les procédures administratives"),
    (1, "Demander la planification des retraits", "-", "Au plus tard Juin A-2 (400kV) ou A-1 (<= 225kV)", "Mener les études d'ingénierie détaillées pour un projet LA/LS"),
    (1, "Réaliser le Bilan de Projet", "-", "", "Clôturer le projet"),
    (1, "Réaliser le suivi Patrimoine", "-", "", "Préparer et réaliser la MEC"),
    (1, "Réaliser une réunion préparatoire", "-", "", "Réaliser les travaux"),
    (1, "Demander la planification des retraits", "-", "", "Mener les études d'ingénierie détaillées pour un projet Poste/CC"),
    (1, "Passer en revue le dossier DO", "-", "", "Mener les études décisionnelles"),
    (2, "Poursuivre ou lancer la recherche du patrimoine juridique", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (2, "Obtenir l'accès légal aux terrains", "-", "", "Mener la concertation et les procédures administratives"),
    (2, "Demander les prestations internes Travaux", "-", "Au plus tard Juin A-1", "Mener les études d'ingénierie détaillées pour un projet LA/LS"),
    (2, "Solder les commandes dans GCP", "-", "", "Clôturer le projet"),
    (2, "Elaborer le dossier de remise d'ouvrage", "-", "", "Préparer et réaliser la MEC"),
    (2, "Préparer et organiser les visites d'inspection commune", "-", "", "Réaliser les travaux"),
    (2, "Demander les prestations internes Travaux", "-", "", "Mener les études d'ingénierie détaillées pour un projet Poste/CC"),
    (2, "Mise à jour du CCF si besoin", "-", "", "Mener les études décisionnelles"),
    (3, "Réaliser l'étude de contexte", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (3, "Obtenir les autorisations de détail", "-", "", "Mener la concertation et les procédures administratives"),
    (3, "Contractualiser les Etudes", "-", "3 mois", "Mener les études d'ingénierie détaillées pour un projet LA/LS"),
    (3, "Clôturer les plans de contrôle et le projet dans Escorte", "-", "", "Clôturer le projet"),
    (3, "Préparer le point d'arrêt P4", "-", "", "Préparer et réaliser la MEC"),
    (3, "Réaliser la réunion d'ouverture de chantier", "-", "", "Réaliser les travaux"),
    (3, "Réaliser les études préalables", "-", "", "Mener les études d'ingénierie détaillées pour un projet Poste/CC"),
    (3, "Réaliser la revue patrimoniale", "-", "", "Mener les études décisionnelles"),
    (4, "Réaliser la revue patrimoniale", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (4, "Contractualiser la prestation CSPS / AEU", "-", "", "Mener les études d'ingénierie détaillées pour un projet LA/LS"),
    (4, "Mettre les engagements / dépenses futures à 0 dans SIEPR et prendre la photo dernière mise en service", "-", "", "Clôturer le projet"),
    (4, "Remettre l'ouvrage au GMR", "-", "", "Préparer et réaliser la MEC"),
    (4, "Réaliser le suivi Patrimoine", "-", "", "Réaliser les travaux"),
    (4, "Contractualiser les Etudes et Travaux", "-", "", "Mener les études d'ingénierie détaillées pour un projet Poste/CC"),
    (4, "Réaliser le réunion de lancement du projet", "-", "", "Mener les études décisionnelles"),
    (5, "Contractualiser les études pour acquérir la description du patrimoine et de connaissance du patrimoine technique", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (5, "Piloter les Etudes externalisées", "-", "LA: 9 mois LS: 1 an", "Mener les études d'ingénierie détaillées pour un projet LA/LS"),
    (5, "Vérifier la résorption des écarts patrimoniaux et des anomalies CMEE/CVS", "-", "", "Clôturer le projet"),
    (5, "Réaliser le point d'arrêt P4", "-", "", "Préparer et réaliser la MEC"),
    (5, "Piloter la réalisation des travaux", "-", "", "Réaliser les travaux"),
    (5, "Contractualiser la prestation CSPS / AEU", "-", "", "Mener les études d'ingénierie détaillées pour un projet Poste/CC"),
    (5, "Définir la catégorie du projet et les exigences de management de projet associées", "-", "", "Mener les études décisionnelles"),
    (6, "Réaliser la revue d'étude vétusté", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (6, "Construire le planning de réalisation du projet", "-", "", "Mener les études d'ingénierie détaillées pour un projet LA/LS"),
    (6, "Vérifier que les engagements vis-à-vis de l'externe sont terminés", "-", "", "Clôturer le projet"),
    (6, "Réceptionner les prestations", "-", "", "Préparer et réaliser la MEC"),
    (6, "Piloter les études externalisées", "-", "", "Mener les études d'ingénierie détaillées pour un projet Poste/CC"),
    (6, "Elaborer la CTF", "-", "", "Mener les études décisionnelles"),
    (7, "Réaliser les études paramétriques", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (7, "Demander les prestations internes Etudes pour l'APD", "-", "", "Mener les études d'ingénierie détaillées pour un projet LA/LS"),
    (7, "Saisir la demande de blocage imputations / pointage technique", "-", "", "Clôturer le projet"),
    (7, "Déclarer la conformité de l'ouvrage", "-", "", "Préparer et réaliser la MEC"),
    (7, "Construire le planning de réalisation du projet", "-", "", "Mener les études d'ingénierie détaillées pour un projet Poste/CC"),
    (7, "Valider le point d'arret P1", "-", "", "Mener les études décisionnelles"),
    (8, "Demander les prestations Internes Etudes", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (8, "Réaliser l'Avant Projet Détaillé (APD)", "-", "", "Mener les études d'ingénierie détaillées pour un projet LA/LS"),
    (8, "Préparer le dossier d'archivage", "-", "", "Clôturer le projet"),
    (8, "Demander les prestations internes Etudes pour l'APD", "-", "", "Mener les études d'ingénierie détaillées pour un projet Poste/CC"),
    (8, "Faire valider la décision ou PTF, voir l'absence de DCT", "-", "", "Mener les études décisionnelles"),
    (9, "Examiner la consignabilité de l'ouvrage et les modalités d'exploitation", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (9, "Présenter l'APD au GMR", "-", "", "Mener les études d'ingénierie détaillées pour un projet LA/LS"),
    (9, "Transmettre le(s) dossier(s) d'ouvrage(s) au GMR", "-", "", "Clôturer le projet"),
    (9, "Réaliser l'APD", "-", "", "Mener les études d'ingénierie détaillées pour un projet Poste/CC"),
    (9, "Rédiger et faire signer la DCT", "-", "", "Mener les études décisionnelles"),
    (10, "Elaborer la NOS", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (10, "Finaliser l'APD", "-", "", "Mener les études d'ingénierie détaillées pour un projet LA/LS"),
    (10, "Saisir la demande de clôture", "-", "", "Clôturer le projet"),
    (10, "Présenter l'APD au GMR", "-", "", "Mener les études d'ingénierie détaillées pour un projet Poste/CC"),
    (11, "Déterminer le chiffrage de base (ECV ou RCD) et réaliser l'analyse de risques", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (11, "Point d'arrêt P2", "-", "", "Mener les études d'ingénierie détaillées pour un projet LA/LS"),
    (11, "Finaliser l'APD", "-", "", "Mener les études d'ingénierie détaillées pour un projet Poste/CC"),
    (12, "Réaliser un point d'arrêt (avec le Directeur de Réalisation) pour valider la stratégie et confirmer la catégorie du projet", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (12, "Valider le point d'arrêt P2", "-", "", "Mener les études d'ingénierie détaillées pour un projet Poste/CC"),
    (12, "Contractualiser les travaux", "-", "", "Mener les études d'ingénierie détaillées pour un projet LA/LS"),
    (13, "Constituer le dossier et faire valider la DCT", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (13, "Réaliser un échange sécurité avec le prestataire et le CSPS / AEU", "-", "", "Mener les études d'ingénierie détaillées pour un projet LA/LS"),
    (13, "Faire valider la DI", "-", "", "Mener les études d'ingénierie détaillées pour un projet Poste/CC"),
    (14, "Contractualiser ou lancer les études de détails (et études complémentaires)", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (14, "Faire valider la décision d'investissement", "-", "", "Mener les études d'ingénierie détaillées pour un projet LA/LS"),
    (15, "Contrôler les études, faire les choix des travaux et des écarts à traiter", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (16, "Demander l'attribution du prestataire travaux et contractualiser avec le GIE Tvx attribué", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (17, "Mener la concertation (stratégique et opérationnelle) et obtenir les autorisations administratives préalables", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (18, "Organiser la réunion tri-partite pour réaliser l'examen du DT v1 et analyser la sécurité du projet", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (19, "Finaliser la proposition de solution technique (et ses possibles variantes) et en faire les études de mise en oeuvre", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (20, "Lancer ou poursuivre le conventionnement", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (21, "Constituer l'Avant Projet Détaillé (APD)", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (22, "Présenter l'APD au GMR", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (23, "Finaliser l'APD", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (24, "Valider le point d'arrêt P2", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (25, "Faire valider la DI", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (26, "Réaliser un échange sécurité avec le CSPS / AEU", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)"),
    (27, "Contractualiser les Travaux", "-", "", "Mener les études décisionnelles et d'ingénierie détaillées pour un projet de réhabilitation LA (GAELA)")
]

@transaction.atomic
def create_process_data():
    try:
        # Suppression des données existantes
        print("Nettoyage des données existantes...")
        ProcessusEtape.objects.all().delete()

        # Création des étapes
        print("\nCréation des étapes du processus...")
        etapes = {}
        for ordre_global, nom in ETAPES_DATA:
            etape = ProcessusEtape.objects.create(
                nom=nom,
                ordre_global=ordre_global,
                ordre=ordre_global,
                actif=True
            )
            etapes[nom] = etape
            print(f"Étape créée : {ordre_global} - {nom}")

        # Création des actions
        print("\nCréation des actions...")
        for ordre, titre, description, delai, etape_nom in ACTIONS_DATA:
            etape = etapes[etape_nom]
            Action.objects.create(
                ordre=ordre,
                titre=titre,
                description=description,
                delai=delai,
                etape=etape
            )
            print(f"Action créée : {titre}")

        print("\nCréation des données terminée avec succès!")

    except Exception as e:
        print(f"\nErreur lors de la création des données : {str(e)}")
        raise

if __name__ == '__main__':
    create_process_data()