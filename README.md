# zkillboardWebhookDiscordKill
Suivi des Kills de Corporation

Ce script Python permet de suivre les kills (destructions de vaisseaux) des corporations spécifiées dans le jeu EVE Online et d'envoyer des notifications via un webhook Discord.
Fonctionnalités

    Récupération des Kills : Le script récupère les données des kills récents pour les corporations spécifiées via l'API de zKillboard.
    Notification Discord : Les détails des kills sont envoyés à un canal Discord via un webhook.
    Base de Données SQLite : Les IDs des kills déjà traités sont stockés dans une base de données SQLite pour éviter les doublons.
    Cache des Noms : Utilisation d'un cache pour les noms des vaisseaux, systèmes, corporations, etc., pour réduire les appels à l'API ESI.

Configuration

    CORP_IDS : Liste des IDs des corporations à suivre.
    WEBHOOK_URL : URL du webhook Discord pour envoyer les notifications.
    ESI_URL : URL de base pour les appels à l'API ESI.
    MAX_KILLS : Nombre maximum de kills à traiter par corporation.

Dépendances

    requests : Pour effectuer des requêtes HTTP.
    sqlite3 : Pour interagir avec la base de données SQLite.
    collections : Pour utiliser defaultdict.

Utilisation

    Installez les dépendances nécessaires :

pip install requests

Configurez les constantes CORP_IDS et WEBHOOK_URL avec les valeurs appropriées.

Exécutez le script :

    python script_name.py

Remarques

    Assurez-vous que le webhook Discord est correctement configuré et que l'URL est valide.
    Le script inclut des délais (time.sleep(1)) pour éviter de surcharger les API.

README in English
Corporation Kill Tracker

This Python script tracks ship kills for specified corporations in the game EVE Online and sends notifications via a Discord webhook.
Features

    Kill Data Retrieval : The script fetches recent kill data for specified corporations via the zKillboard API.
    Discord Notification : Kill details are sent to a Discord channel via a webhook.
    SQLite Database : IDs of processed kills are stored in an SQLite database to avoid duplicates.
    Name Cache : Uses a cache for ship names, systems, corporations, etc., to reduce API calls to ESI.

Configuration

    CORP_IDS : List of corporation IDs to track.
    WEBHOOK_URL : Discord webhook URL for sending notifications.
    ESI_URL : Base URL for ESI API calls.
    MAX_KILLS : Maximum number of kills to process per corporation.

Dependencies

    requests : For making HTTP requests.
    sqlite3 : For interacting with the SQLite database.
    collections : For using defaultdict.

Usage

    Install the necessary dependencies:

pip install requests

Configure the CORP_IDS and WEBHOOK_URL constants with appropriate values.

Run the script:

    python script_name.py

Notes

    Ensure the Discord webhook is properly configured and the URL is valid.
    The script includes delays (time.sleep(1)) to avoid overloading the APIs.
