# Surveillance température et humidité (DHT11 + ESP8266 + Django)

Application IoT qui mesure la température et l'humidité avec un capteur **DHT11** branché sur une carte **NodeMCU ESP8266**, envoie les mesures en Wi-Fi à un serveur **Django**, les affiche en temps réel dans un tableau de bord web et envoie des **alertes par e-mail (Gmail) et Telegram** quand la température dépasse un seuil.

Projet réalisé dans le cadre du TP Django / IoT : alertes Gmail et Telegram.

## Fonctionnalités

- Lecture du DHT11 par l'ESP8266 toutes les 10 secondes.
- Envoi des mesures en JSON (requête HTTP POST) vers une API Django REST.
- Enregistrement des mesures dans une base SQLite.
- Tableau de bord en temps réel (rafraîchi toutes les 5 secondes) :
  - cartes avec la dernière température, la dernière humidité et le nombre d'incidents ;
  - deux graphiques séparés et placés côte à côte (température à gauche, humidité à droite) ;
  - tableau de suivi des incidents (Temps, Température, Incident, Compteur, Op1, Op2, Op3).
- Alerte automatique par **e-mail Gmail** et par **message Telegram** quand la température dépasse 25 °C.

## Architecture

```
DHT11 ──► ESP8266 (NodeMCU) ──Wi-Fi 2,4 GHz──► Django (API REST) ──► SQLite
                                                    │
                                                    ├──► Tableau de bord (navigateur)
                                                    └──► Alertes Gmail + Telegram
```

## Matériel

- Carte NodeMCU ESP8266 (module ESP-12E)
- Capteur DHT11 (version à 4 broches : ajouter une résistance de 10 kΩ entre DATA et VCC si les lectures échouent)
- Breadboard et fils
- Câble micro-USB

### Câblage

| DHT11 | NodeMCU |
|---|---|
| VCC | 3V3 |
| DATA | D2 (GPIO4) |
| GND | GND |

> L'ESP8266 ne fonctionne qu'en **Wi-Fi 2,4 GHz**. Il ne peut pas se connecter à un réseau 5 GHz.

## Logiciels requis

- Python 3.10 ou plus récent
- Django et Django REST Framework
- `pyTelegramBotAPI` (alertes Telegram)
- Arduino IDE avec :
  - le gestionnaire de cartes **esp8266** (carte à choisir : *NodeMCU 1.0 (ESP-12E Module)*) ;
  - les bibliothèques **DHT sensor library** et **Adafruit Unified Sensor**.

## Installation du serveur Django

```bash
# 1. Cloner le dépôt
git clone https://github.com/VOTRE_COMPTE/VOTRE_DEPOT.git
cd VOTRE_DEPOT

# 2. Créer et activer un environnement virtuel
python -m venv .venv
# Windows (PowerShell) :
.venv\Scripts\Activate.ps1
# Linux / macOS :
source .venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Créer la base de données
python manage.py migrate

# 5. Lancer le serveur (accessible depuis le réseau local)
python manage.py runserver 0.0.0.0:8000
```

Le tableau de bord est ensuite disponible sur `http://127.0.0.1:8000/`, et depuis un autre appareil du même réseau sur `http://IP_DU_PC:8000/`.

Pour connaître l'adresse IP du PC : `ipconfig` (Windows) ou `ip a` (Linux), ligne « Adresse IPv4 » de la carte Wi-Fi.

## Configuration des alertes

Les réglages se trouvent dans `projet/settings.py`. **Ne publiez jamais vos vrais identifiants** : utilisez des variables d'environnement ou un fichier non versionné.

### Gmail

1. Activer la validation en deux étapes sur le compte Google.
2. Créer un **mot de passe d'application** : <https://myaccount.google.com/apppasswords>.
3. Renseigner dans `settings.py` :

```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 10
EMAIL_HOST_USER = "votre_adresse@gmail.com"
EMAIL_HOST_PASSWORD = "mot_de_passe_application"
```

### Telegram

1. Dans Telegram, créer un bot avec **@BotFather** (`/newbot`) et copier le token.
2. Envoyer `/start` au bot, puis ouvrir `https://api.telegram.org/botVOTRE_TOKEN/getUpdates` pour lire votre `chat id`.
3. Renseigner dans `settings.py` :

```python
TELEGRAM_TOKEN = "token_du_bot"
TELEGRAM_CHAT_ID = "votre_chat_id"
```

### Seuil d'alerte

L'alerte est déclenchée dans `DHT/views.py` (classe `Dhtviews`) quand `temp > 25`. Modifiez cette valeur pour changer le seuil.

## Programmation de l'ESP8266

Le code Arduino se trouve dans `arduino/dht_esp8266.ino`. Avant de le téléverser, renseigner :

```cpp
#define DHTPIN D2
const char* WIFI_SSID = "NOM_DU_WIFI_2_4GHZ";
const char* WIFI_PASSWORD = "MOT_DE_PASSE_WIFI";
const char* SERVER_URL = "http://IP_DU_PC:8000/api/post/";
```

Le JSON envoyé doit utiliser exactement les clés du modèle Django :

```json
{"temp": 24.3, "hum": 51.0}
```

Après le téléversement, ouvrir le moniteur série à **115200 bauds** : `Code HTTP : 201` signifie que la mesure est bien enregistrée.

> Si l'adresse IP du PC change (autre réseau, nouvelle connexion), il faut la corriger dans `SERVER_URL` puis téléverser à nouveau le code.

## API

| Méthode | URL | Description |
|---|---|---|
| `POST` | `/api/post/` | Enregistre une mesure (`temp`, `hum`) et déclenche l'alerte si `temp > 25` |
| `GET` | `/api/get/` | Renvoie les 50 dernières mesures, de la plus récente à la plus ancienne |
| `GET` | `/` | Tableau de bord |

Exemple de test sans la carte (PowerShell) :

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/post/ -Method Post -ContentType "application/json" -Body '{"temp":30,"hum":50}'
```

Exemple de réponse de `GET /api/get/` :

```json
{
  "data": [
    {"id": 3, "temp": 25.5, "hum": 60.0, "date": "2026-11-11T21:24:24.167110Z"}
  ]
}
```

## Détection des incidents (tableau de bord)

Le tableau de suivi applique les règles suivantes à chaque mesure :

| Colonne | Règle |
|---|---|
| **Incident** | 1 si la température est supérieure au seuil maximum ou inférieure au seuil minimum, sinon 0 |
| **Compteur** | +1 à chaque mesure consécutive en incident, remis à 0 quand la température redevient normale |
| **Op1 / Op2 / Op3** | passent à 1 quand le compteur atteint respectivement 1, 4 et 7 |

Un **incident** correspond à un épisode complet : le nombre d'incidents affiché est le nombre de fois où le compteur passe à 1.

Les réglages sont au début du script de `DHT/templates/DHT/dashboard.html` :

```javascript
const SEUIL_MAX = 25;       // incident si température > SEUIL_MAX
const SEUIL_MIN = 15;       // ou si température < SEUIL_MIN
const NIVEAUX = [1, 4, 7];  // compteur à atteindre pour Op1, Op2, Op3
const MAX_LIGNES = 15;      // nombre de lignes affichées dans le tableau
```

## Structure du projet

```
.
├── arduino/
│   └── dht_esp8266.ino          # code de l'ESP8266
├── DHT/
│   ├── migrations/
│   ├── static/DHT/chart.umd.js  # Chart.js 4.4.7 (copie locale, fonctionne sans Internet)
│   ├── templates/DHT/dashboard.html
│   ├── models.py                # modèle Dht11 (temp, hum, date)
│   ├── serializers.py
│   ├── views.py                 # API, tableau de bord, alertes
│   └── urls.py
├── projet/
│   ├── settings.py
│   └── urls.py
├── manage.py
└── requirements.txt
```

## Dépannage

| Problème | Piste |
|---|---|
| La carte n'arrive pas à se connecter | Le Wi-Fi doit être en 2,4 GHz. Avec un iPhone : activer « Compatibilité maximale » dans Partage de connexion |
| `Code HTTP : -1` sur la carte | Serveur arrêté, mauvaise IP dans `SERVER_URL`, ou pare-feu qui bloque le port 8000 |
| `Code HTTP : 400` | Les clés du JSON ne sont pas `temp` et `hum` |
| `Erreur lecture DHT11` | Vérifier le câblage et la broche (`DHTPIN`), ajouter une résistance de 10 kΩ entre DATA et VCC |
| `That IP address can't be assigned to` au lancement | Utiliser `runserver 0.0.0.0:8000` |
| `Unable to connect to the remote server` (test PowerShell) | Le serveur Django n'est pas lancé, ou il écoute sur une autre adresse |
| `ImproperlyConfigured ... MAILERS` | Supprimer le bloc `MAILERS` de `settings.py` (incompatible avec les réglages `EMAIL_*`) |
| `SMTPAuthenticationError` | Mot de passe d'application Gmail incorrect (à copier sans espaces) |
| Pas de mail ni de message Telegram | Le PC doit avoir accès à Internet. Les erreurs s'affichent dans le terminal de Django |
| Graphiques absents | Vérifier que `DHT/static/DHT/chart.umd.js` existe, puis redémarrer le serveur |

## Vider la base de données

```bash
python manage.py shell
```

```python
from DHT.models import Dht11
Dht11.objects.all().delete()
exit()
```

## Sécurité

- Ne publiez pas `settings.py` avec une vraie `SECRET_KEY`, un mot de passe d'application Gmail ou un token Telegram.
- Ne publiez pas le mot de passe de votre Wi-Fi dans le code Arduino.
- `DEBUG = True` et `ALLOWED_HOSTS = ['*']` sont réservés au développement.
- Si un secret a été publié par erreur, révoquez-le (mot de passe d'application Google, `/revoke` dans BotFather) puis créez-en un nouveau.

## Technologies

Python, Django, Django REST Framework, SQLite, Chart.js, Arduino (C++), ESP8266, DHT11, Gmail SMTP, Telegram Bot API.

## Auteur

[Votre nom] , GSI.
