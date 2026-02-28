# Forex Fibonacci Bot 🤖

Bot Telegram automatisé pour les signaux Forex basé sur une stratégie Fibonacci multi-timeframes.

## 🎯 Caractéristiques

- **Analyse Multi-Timeframe**: Weekly, Daily, Hourly
- **Stratégie Fibonacci**: Détection automatique des retracements 0.500-0.618
- **Confirmation Heiken Ashi**: Validation des signaux avec bougies Heiken Ashi
- **14 Paires Forex**: EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD, NZD/USD, EUR/GBP, EUR/JPY, GBP/JPY, AUD/JPY, EUR/CHF, GBP/CHF, CAD/JPY
- **Optimisation API**: Respect du budget 800 crédits/jour Twelve Data
- **Notifications Telegram**: Alertes en temps réel
- **Historique SQLite**: Sauvegarde de tous les signaux

## 📋 Prérequis

- Python 3.8+
- Compte Telegram avec bot créé
- Clé API Twelve Data (gratuite)

## 🚀 Installation

### 1. Cloner le projet

```bash
cd /home/ubuntu/fibo_bot
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configurer les variables d'environnement

Créer un fichier `.env` à partir du template:

```bash
cp .env.example .env
```

Éditer `.env` et ajouter vos clés:

```env
TELEGRAM_TOKEN_FIBOBOT=your_telegram_bot_token
TWELVEDATA_API_KEY_FIBOBOT=your_twelvedata_api_key
LOG_LEVEL=INFO
TIMEZONE=UTC
SCAN_TIME_DAILY=00:00
```

### 4. Démarrer le bot

```bash
python main.py
```

## 🔧 Configuration

### Variables d'environnement

| Variable | Description | Exemple |
|----------|-------------|---------|
| `TELEGRAM_TOKEN_FIBOBOT` | Token du bot Telegram | `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11` |
| `TWELVEDATA_API_KEY_FIBOBOT` | Clé API Twelve Data | `demo` |
| `LOG_LEVEL` | Niveau de log | `INFO`, `DEBUG`, `WARNING` |
| `TIMEZONE` | Timezone | `UTC` |
| `SCAN_TIME_DAILY` | Heure du scan quotidien (UTC) | `00:00` |

### Paramètres techniques

Éditer `config/settings.py`:

```python
SMA_PERIOD = 200                    # Période SMA
RSI_PERIOD = 14                     # Période RSI
FIBONACCI_ZONE_MIN = 0.500          # Zone GA min
FIBONACCI_ZONE_MAX = 0.618          # Zone GA max
TWELVEDATA_CREDITS_DAILY_LIMIT = 800
```

## 📊 Commandes Telegram

| Commande | Description |
|----------|-------------|
| `/start` | Démarrer le bot |
| `/status` | Statut des paires alignées et crédits API |
| `/pairs` | Statut détaillé des 14 paires |
| `/history` | Derniers signaux (24h) |
| `/stats` | Performance (weekend uniquement) |

## 🔄 Logique de détection

### Étape 1: Scan quotidien W1+D1 (00:00 UTC)

1. Récupérer prix et SMA200 pour les 14 paires
2. Classifier chaque paire:
   - **BULLISH**: Prix > SMA200 sur W1 ET D1
   - **BEARISH**: Prix < SMA200 sur W1 ET D1
   - **NEUTRAL**: Non aligné

### Étape 2: Scan H1 (toutes les heures)

Uniquement sur les paires alignées (BULLISH ou BEARISH)

**Mode ACHAT (BULLISH)**:
- Dernier sommet = Heiken Ashi rouge→vert
- Tracer Fibonacci (creux → sommet)
- Prix dans zone [0.500, 0.618]?

**Mode VENTE (BEARISH)**:
- Dernier creux = Heiken Ashi vert→rouge
- Tracer Fibonacci (sommet → creux)
- Prix dans zone [0.500, 0.618]?

### Étape 3: Gestion Zone (GA)

| Événement | Action |
|-----------|--------|
| Prix entre dans [0.500, 0.618] | Notifier "PRIX DANS GA" |
| Heiken Ashi couleur opposée dans zone | Notifier "SETUP CONFIRMÉ" |
| Corps bougie ferme hors zone | Notifier "GA CASSÉE" |

### Étape 4: Bonus

- Divergence RSI (14 périodes)
- Confluence support/résistance (50 dernières bougies H1)

## 📈 Messages Telegram

### Prix dans GA

```
⚠️ [EUR/USD] - Prix dans GA 0.500-0.618
Zone: 1.08500 - 1.08720 | Prix: 1.08615
Direction: ACHAT | Status: En attente confirmation...
```

### Setup confirmé

```
📊 [EUR/USD] - SETUP ACHAT
├─ Filtres W1/D1: ✅ BULLISH
├─ GA: 0.500-0.618 [1.08500 - 1.08720]
├─ Heiken Ashi: Haussier ✅
├─ Prix: 1.08615
├─ RSI: Divergence haussière 🟢
└─ S/R: Confluence 1.08550 🟢
```

### GA cassée

```
❌ [EUR/USD] - GA cassée
Zone invalidée | Prix: 1.08850 | Setup annulé
```

### Résumé daily

```
📅 [2024-02-24] - Paires alignées
🟢 BULLISH: EUR/USD, GBP/USD, AUD/USD (3)
🔴 BEARISH: USD/JPY, USD/CHF (2)
⚪ NEUTRE: 9 paires
Prochains scans: EUR/USD, GBP/USD, AUD/USD, USD/JPY, USD/CHF
```

## 🗄️ Base de données

SQLite avec tables:

- `signals`: Historique des signaux détectés
- `pair_status`: Statut actuel des paires (W1, D1, SMA)
- `active_zones`: Zones Fibonacci actives

## 🧪 Tests

Exécuter les tests:

```bash
python tests.py
```

Tests couverts:
- Calcul des niveaux Fibonacci
- Détection de pics et creux
- Conversion Heiken Ashi
- Calcul SMA et RSI
- Détection support/résistance

## 📊 Architecture

```
fibo_bot/
├── config/
│   ├── settings.py          # Paramètres
│   └── secrets.py           # Variables d'environnement
├── core/
│   ├── scanner.py           # Logique scan multi-timeframe
│   ├── fibonacci.py         # Calculs Fibonacci
│   ├── heiken_ashi.py       # Analyse Heiken Ashi
│   └── technical.py         # SMA, RSI, S/R
├── data/
│   ├── twelvedata_client.py # Client API + rate limiting
│   └── database.py          # SQLite
├── bot/
│   ├── telegram_bot.py      # Gestion bot Telegram
│   └── handlers.py          # Commandes
├── scheduler/
│   └── jobs.py              # Scans automatiques
├── utils/
│   └── logger.py            # Logging
├── main.py                  # Point d'entrée
├── tests.py                 # Tests unitaires
├── requirements.txt
├── .env.example
└── README.md
```

## ⚙️ Optimisation API

Budget quotidien: 800 crédits Twelve Data

- **Scan W1+D1**: 112 crédits (00:00 UTC)
  - 14 paires × 4 requêtes (W1 prix + SMA, D1 prix + SMA)
- **Scan H1**: ~14 crédits/heure (paires alignées)
- **Total**: ~500 crédits/jour

## 🔒 Sécurité

- Lecture automatique des variables d'environnement
- Rate limiting: max 8 req/min Twelve Data
- Retry 3x avec backoff exponentiel
- Logs rotatifs (10 MB max)
- Pas de stockage de clés en dur

## 📝 Logs

Les logs sont stockés dans `logs/fibo_bot.log` avec rotation automatique.

Niveaux:
- `DEBUG`: Informations détaillées
- `INFO`: Événements importants
- `WARNING`: Avertissements
- `ERROR`: Erreurs

## 🛑 Arrêt du bot

```bash
# Ctrl+C pour arrêter proprement
```

Le bot arrête le scheduler et ferme les connexions correctement.

## 🐛 Dépannage

### Erreur: "TELEGRAM_TOKEN_FIBOBOT n'est pas défini"

Vérifier que le fichier `.env` existe et contient la clé:

```bash
cat .env | grep TELEGRAM_TOKEN_FIBOBOT
```

### Erreur: "TWELVEDATA_API_KEY_FIBOBOT n'est pas défini"

Vérifier la clé API Twelve Data:

```bash
cat .env | grep TWELVEDATA_API_KEY_FIBOBOT
```

### Pas de signaux détectés

1. Vérifier les logs: `tail -f logs/fibo_bot.log`
2. Vérifier les crédits API: `/status`
3. Vérifier les paires alignées: `/pairs`

## 📞 Support

Pour les problèmes:

1. Vérifier les logs
2. Exécuter les tests: `python tests.py`
3. Vérifier la configuration

## 📄 Licence

MIT

## 🎓 Stratégie

Stratégie Fibonacci multi-timeframes:

1. **Confirmation W1+D1**: Alignement SMA200
2. **Détection H1**: Retracements Fibonacci 0.500-0.618
3. **Validation**: Heiken Ashi + RSI + S/R

Risque: Moyen | Rendement: Variable selon les conditions de marché

---

**Bot Fibonacci v1.0** - Prêt à démarrer avec `python main.py`
