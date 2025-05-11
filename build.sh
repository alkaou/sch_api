#!/bin/bash

# Script pour installer les dépendances système pour WeasyPrint sur Vercel

echo "Installation des dépendances système pour WeasyPrint..."

# Mettre à jour la liste des paquets et installer les dépendances
# Les paquets exacts peuvent varier légèrement selon l'image de base de Vercel,
# mais ceux-ci sont généralement les requis pour WeasyPrint sur des systèmes basés sur Debian.
apt-get update -y && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libharfbuzz0b \
    libpangocairo-1.0-0 \
    shared-mime-info \
    # Ajoutez d'autres dépendances si nécessaire (ex: libffi-dev, python3-dev pour certaines roues Python)
    # fontconfig # Utile pour la gestion des polices

echo "Dépendances système installées."

# (Optionnel) Vous pouvez ajouter ici d'autres commandes de build, comme la collecte de fichiers statiques si vous en aviez.
# python manage.py collectstatic --noinput # Exemple Django, non applicable ici mais illustre le concept

# Assurez-vous que le script se termine avec un code de sortie 0 en cas de succès
exit 0