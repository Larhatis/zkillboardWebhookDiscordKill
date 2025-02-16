
import requests
import time
import sqlite3
from collections import defaultdict

# Constantes
CORP_IDS = ["ID_corporation", "ID_corporation", "ID_corporation", "ID_corporation"]
WEBHOOK_URL = "https://discord.com/api/webhooks/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
ESI_URL = "https://esi.evetech.net/latest/killmails/"
MAX_KILLS = 10

name_cache = defaultdict(str)

def format_isk(value):
    try:
        return f"{float(value):,.2f} ISK"
    except:
        return "Valeur inconnue"

def setup_database():
    conn = sqlite3.connect('killmails.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seen_kills (
            kill_id INTEGER PRIMARY KEY
        )
    ''')
    conn.commit()
    return conn

def load_seen_ids(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT kill_id FROM seen_kills")
    return set(row[0] for row in cursor.fetchall())

def save_kill_id(conn, kill_id):
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO seen_kills (kill_id) VALUES (?)", (kill_id,))
    conn.commit()

def send_discord_webhook(kill_data):
    victim_corp_link = f"https://zkillboard.com/corporation/{kill_data['victim_corp_id']}/" if kill_data['victim_corp_id'] else ""
    attacker_corp_link = f"https://zkillboard.com/corporation/{kill_data['attacker_corp_id']}/" if kill_data['attacker_corp_id'] else ""

    embed = {
        "title": f"💥 {kill_data['ship_name']} détruit par {kill_data['attacker_name']} ({kill_data['attacker_corp_name']})",
        "color": 65280,  # Vert (couleur pour les kills)
        "fields": [
            {
                "name": "Détruit par",
                "value": f"**{kill_data['attacker_name']}**\n[{kill_data['attacker_corp_name']}]({attacker_corp_link})",
                "inline": True
            },
            {
                "name": "Victime",
                "value": f"**{kill_data['victim_name']}**\n[{kill_data['victim_corp_name']}]({victim_corp_link})",
                "inline": True
            },
            {
                "name": "📊 Pertes",
                "value": (
                    f"**Valeur totale détruite:** {kill_data['destroyed_value']}\n"
                    f"🔴 **Valeur Dropped:** {kill_data['dropped_value']}\n"
                    f"**Système:** {kill_data['system']}\n"
                    f"**Date:** {kill_data['timestamp']}"
                ),
                "inline": False
            },
            {
                "name": "🔗 Lien du killmail",
                "value": f"[zkillboard.com]({kill_data['zkill_link']})",
                "inline": False
            }
        ],
        "thumbnail": {"url": f"https://images.evetech.net/types/{kill_data['ship_id']}/render"}
    }

    payload = {
        "embeds": [embed],
        "username": "Corp Kill Tracker",
        "avatar_url": "https://i.imgur.com/3cZKW7h.png"
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Erreur webhook: {str(e)}")

def get_names(ids):
    global name_cache
    uncached_ids = [id for id in ids if id not in name_cache]
    if uncached_ids:
        try:
            response = requests.post(
                "https://esi.evetech.net/latest/universe/names/",
                json=list(uncached_ids),
                headers={"User-Agent": "CorpKillTracker/1.0"}
            )
            if response.status_code == 200:
                for item in response.json():
                    name_cache[item['id']] = item['name']
        except Exception as e:
            print(f"Erreur lors de la résolution des noms: {str(e)}")
    return name_cache

def get_corp_kills():
    conn = setup_database()
    seen_ids = load_seen_ids(conn)
    new_kills = 0

    for corp_id in CORP_IDS:
        try:
            zkill_url = f"https://zkillboard.com/api/corporationID/{corp_id}/kills/"
            response = requests.get(zkill_url, headers={"Accept-Encoding": "gzip"})
            killmails = response.json()[:MAX_KILLS]

            for km in reversed(killmails):
                try:
                    kill_id = km['killmail_id']
                    if kill_id in seen_ids:
                        continue

                    details = requests.get(
                        f"{ESI_URL}{kill_id}/{km['zkb']['hash']}/",
                        params={"datasource": "tranquility"}
                    ).json()

                    # Extraction des valeurs
                    destroyed_value = format_isk(km['zkb'].get('destroyedValue'))
                    dropped_value = format_isk(km['zkb'].get('droppedValue'))

                    # Résolution des noms
                    victim = details['victim']
                    attacker = next((a for a in details['attackers'] if a.get('final_blow')), {})

                    ids = {
                        victim.get('ship_type_id'),
                        victim.get('corporation_id'),
                        victim.get('character_id'),
                        details.get('solar_system_id'),
                        attacker.get('corporation_id'),
                        attacker.get('character_id')
                    } - {None}

                    names = get_names(ids)

                    kill_data = {
                        "kill_id": kill_id,
                        "ship_id": victim['ship_type_id'],
                        "ship_name": names.get(victim['ship_type_id'], 'Vaisseau inconnu'),
                        "victim_name": names.get(victim.get('character_id'), 'NPC'),
                        "victim_corp_id": victim.get('corporation_id'),
                        "victim_corp_name": names.get(victim.get('corporation_id'), 'Corporation inconnue'),
                        "attacker_name": names.get(attacker.get('character_id'), 'NPC'),
                        "attacker_corp_id": attacker.get('corporation_id'),
                        "attacker_corp_name": names.get(attacker.get('corporation_id'), 'Corporation inconnue'),
                        "destroyed_value": destroyed_value,
                        "dropped_value": dropped_value,
                        "system": names.get(details['solar_system_id'], 'Système inconnu'),
                        "timestamp": details['killmail_time'].replace('T', ' ').replace('Z', ' UTC'),
                        "zkill_link": f"https://zkillboard.com/kill/{kill_id}/"
                    }

                    send_discord_webhook(kill_data)
                    save_kill_id(conn, kill_id)
                    new_kills += 1
                    time.sleep(1)

                except Exception as e:
                    print(f"Erreur traitement kill {kill_id}: {str(e)}")
                    continue

        except Exception as e:
            print(f"ERREUR pour la corporation {corp_id}: {str(e)}")

    print(f"Analyse terminée. {new_kills} nouveau(x) kill(s) détecté(s).")
    conn.close()

if __name__ == "__main__":
    get_corp_kills()
