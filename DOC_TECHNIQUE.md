# Documentation Technique - Forex Fibonacci Bot

## 📊 Flowchart Logique Générale

```
┌─────────────────────────────────────────────────────────────┐
│                    BOT FIBONACCI DÉMARRAGE                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │  Initialisation Composants         │
        │  - API Twelve Data                 │
        │  - Base de données SQLite          │
        │  - Bot Telegram                    │
        │  - Scheduler APScheduler           │
        └────────────┬───────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────────┐
        │  Démarrage Scheduler               │
        │  - Scan quotidien W1+D1 (00:00)    │
        │  - Scan H1 (toutes les heures)     │
        │  - Heartbeat (6h)                  │
        └────────────┬───────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────────┐
        │  En attente d'événements           │
        │  (Polling Telegram)                │
        └────────────────────────────────────┘
```

## 🔄 Scan Quotidien W1+D1 (00:00 UTC)

```
SCAN QUOTIDIEN W1+D1
│
├─ Pour chaque paire (14 paires):
│  │
│  ├─ Récupérer bougies Weekly (200 périodes)
│  │  └─ Calculer SMA200 Weekly
│  │
│  ├─ Récupérer bougies Daily (200 périodes)
│  │  └─ Calculer SMA200 Daily
│  │
│  ├─ Récupérer prix actuel (close)
│  │
│  ├─ Déterminer tendance W1:
│  │  ├─ Si prix > SMA200 → BULLISH
│  │  ├─ Si prix < SMA200 → BEARISH
│  │  └─ Si prix = SMA200 → NEUTRAL
│  │
│  ├─ Déterminer tendance D1:
│  │  ├─ Si prix > SMA200 → BULLISH
│  │  ├─ Si prix < SMA200 → BEARISH
│  │  └─ Si prix = SMA200 → NEUTRAL
│  │
│  └─ Vérifier alignement:
│     ├─ Si W1 == D1 et != NEUTRAL → ALIGNÉE
│     │  └─ Ajouter à aligned_pairs
│     └─ Sinon → NEUTRE
│
└─ Envoyer résumé Telegram
   ├─ Nombre BULLISH
   ├─ Nombre BEARISH
   ├─ Nombre NEUTRAL
   └─ Prochains scans H1
```

## 📈 Scan H1 (Toutes les heures)

```
SCAN H1 HORAIRE
│
├─ Pour chaque paire alignée:
│  │
│  ├─ Récupérer bougies H1 (100 périodes)
│  │
│  ├─ Convertir en Heiken Ashi
│  │
│  ├─ Détecter pics et creux
│  │
│  ├─ Si BULLISH:
│  │  │
│  │  ├─ Trouver dernier sommet (peak)
│  │  ├─ Trouver dernier creux (trough)
│  │  │
│  │  ├─ Calculer niveaux Fibonacci:
│  │  │  └─ Levels = Fib(trough → peak)
│  │  │
│  │  ├─ Vérifier prix dans zone [0.500, 0.618]:
│  │  │  ├─ Si OUI → Continuer
│  │  │  └─ Si NON → Passer paire suivante
│  │  │
│  │  ├─ Vérifier Heiken Ashi haussier:
│  │  │  ├─ Si HA close > HA open → Continuer
│  │  │  └─ Sinon → Passer paire suivante
│  │  │
│  │  ├─ Calculer bonus:
│  │  │  ├─ RSI divergence haussière?
│  │  │  └─ Confluence S/R?
│  │  │
│  │  └─ SIGNAL DÉTECTÉ ✅
│  │     └─ Envoyer notification
│  │
│  └─ Si BEARISH:
│     │
│     ├─ Trouver dernier creux (trough)
│     ├─ Trouver dernier sommet (peak)
│     │
│     ├─ Calculer niveaux Fibonacci:
│     │  └─ Levels = Fib(peak → trough)
│     │
│     ├─ Vérifier prix dans zone [0.500, 0.618]:
│     │  ├─ Si OUI → Continuer
│     │  └─ Si NON → Passer paire suivante
│     │
│     ├─ Vérifier Heiken Ashi baissier:
│     │  ├─ Si HA close < HA open → Continuer
│     │  └─ Sinon → Passer paire suivante
│     │
│     ├─ Calculer bonus:
│     │  ├─ RSI divergence baissière?
│     │  └─ Confluence S/R?
│     │
│     └─ SIGNAL DÉTECTÉ ✅
│        └─ Envoyer notification
│
└─ Fin scan H1
```

## 🧮 Calculs Fibonacci

### Formule des niveaux

```
Différence = High - Low

Pour chaque niveau Fibonacci:
    Niveau = High - (Différence × Ratio)

Ratios standards:
- 0.0% = High
- 23.6% = High - (Diff × 0.236)
- 38.2% = High - (Diff × 0.382)
- 50.0% = High - (Diff × 0.500)  ← Zone GA min
- 61.8% = High - (Diff × 0.618)  ← Zone GA max
- 78.6% = High - (Diff × 0.786)
- 100.0% = Low
```

### Exemple

```
High = 1.10000
Low = 1.08000
Diff = 0.02000

Level 0.500 = 1.10000 - (0.02000 × 0.500) = 1.09000
Level 0.618 = 1.10000 - (0.02000 × 0.618) = 1.08764

Zone GA: [1.08764, 1.09000]
```

## 🕯️ Conversion Heiken Ashi

### Formules

```
HA Close = (Open + High + Low + Close) / 4

HA Open = (HA Open[n-1] + HA Close[n-1]) / 2
          (Pour la première bougie: (Open + Close) / 2)

HA High = MAX(High, HA Open, HA Close)

HA Low = MIN(Low, HA Open, HA Close)
```

### Détection de couleur

```
Haussier (Green): HA Close > HA Open
Baissier (Red):   HA Close < HA Open

Changement:
- Red → Green: Sommet confirmé (bullish)
- Green → Red: Creux confirmé (bearish)
```

## 📊 Calcul SMA200

### Formule

```
SMA200 = (Close[n] + Close[n-1] + ... + Close[n-199]) / 200

Où n = barre actuelle
```

### Utilisation

```
Tendance:
- Prix > SMA200 → BULLISH (achat)
- Prix < SMA200 → BEARISH (vente)
- Prix = SMA200 → NEUTRAL (attendre)
```

## 📈 Calcul RSI (Bonus)

### Formule

```
Changements = Close[n] - Close[n-1]

Gains = MAX(Changement, 0)
Pertes = ABS(MIN(Changement, 0))

Moyenne Gains = SUM(Gains[14]) / 14
Moyenne Pertes = SUM(Pertes[14]) / 14

RS = Moyenne Gains / Moyenne Pertes

RSI = 100 - (100 / (1 + RS))
```

### Divergence RSI

```
Divergence Haussière:
- Prix fait un plus bas
- RSI fait un plus haut
→ Signal haussier potentiel

Divergence Baissière:
- Prix fait un plus haut
- RSI fait un plus bas
→ Signal baissier potentiel
```

## 🏗️ Support/Résistance (Bonus)

### Détection

```
Résistance: Point haut local
- High[n] > High[n-1] ET High[n] > High[n+1]

Support: Point bas local
- Low[n] < Low[n-1] ET Low[n] < Low[n+1]

Confluence: Prix proche (±0.1%) d'un S/R
```

## 🔌 API Twelve Data

### Endpoints utilisés

```
GET /time_series
├─ symbol: EUR/USD
├─ interval: 1week, 1day, 1h
├─ outputsize: 200 (max)
└─ format: JSON

Réponse:
{
  "status": "ok",
  "values": [
    {
      "datetime": "2024-02-24 00:00:00",
      "open": "1.10000",
      "high": "1.10100",
      "low": "1.09900",
      "close": "1.10050",
      "volume": "1000000"
    },
    ...
  ]
}
```

### Rate Limiting

```
Limite: 8 requêtes/minute
Crédits: 1 crédit par requête
Budget: 800 crédits/jour

Optimisation:
- Scan W1+D1: 1 fois/jour (00:00) = 112 crédits
- Scan H1: Paires alignées uniquement = ~14 crédits/heure
- Total: ~500 crédits/jour
```

## 🗄️ Schéma Base de Données

### Table: signals

```sql
CREATE TABLE signals (
    id INTEGER PRIMARY KEY,
    symbol TEXT,              -- EUR/USD
    timeframe TEXT,            -- 1h
    signal_type TEXT,          -- bullish/bearish
    price REAL,                -- 1.10050
    fib_level TEXT,            -- 0.500-0.618
    heiken_ashi_confirmed BOOLEAN,
    rsi_divergence BOOLEAN,
    sr_confluence BOOLEAN,
    created_at TIMESTAMP
);
```

### Table: pair_status

```sql
CREATE TABLE pair_status (
    id INTEGER PRIMARY KEY,
    symbol TEXT UNIQUE,        -- EUR/USD
    trend TEXT,                -- BULLISH/BEARISH/NEUTRAL
    w1_price REAL,
    w1_sma200 REAL,
    d1_price REAL,
    d1_sma200 REAL,
    last_updated TIMESTAMP
);
```

### Table: active_zones

```sql
CREATE TABLE active_zones (
    id INTEGER PRIMARY KEY,
    symbol TEXT,               -- EUR/USD
    zone_type TEXT,            -- bullish/bearish
    high REAL,                 -- Sommet
    low REAL,                  -- Creux
    level_500 REAL,            -- Niveau 0.500
    level_618 REAL,            -- Niveau 0.618
    status TEXT,               -- active/broken
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## 📱 Messages Telegram

### Format HTML

```html
<!-- Titre avec emoji -->
<b>📊 [EUR/USD] - SETUP ACHAT</b>

<!-- Détails -->
├─ Filtres W1/D1: ✅ BULLISH
├─ GA: 0.500-0.618 [1.08500 - 1.08720]
├─ Heiken Ashi: Haussier ✅
├─ Prix: 1.08615
├─ RSI: Divergence haussière 🟢
└─ S/R: Confluence 1.08550 🟢
```

## ⚙️ Gestion des erreurs

### Retry avec backoff

```python
for attempt in range(3):
    try:
        response = api.get_data()
        return response
    except Exception as e:
        wait_time = 2 ** attempt  # 1s, 2s, 4s
        time.sleep(wait_time)
```

### Logging

```
[2024-02-24 00:00:00] INFO - Scan quotidien W1+D1 démarré
[2024-02-24 00:00:01] DEBUG - EUR/USD: BULLISH (W1+D1)
[2024-02-24 00:00:02] INFO - 3 paires alignées
[2024-02-24 01:00:00] INFO - Scan H1 pour 3 paires
[2024-02-24 01:05:00] INFO - Signal détecté: EUR/USD BULLISH
```

## 🔒 Sécurité

### Variables d'environnement

```bash
# Ne JAMAIS hardcoder les clés
TELEGRAM_TOKEN_FIBOBOT=xxx
TWELVEDATA_API_KEY_FIBOBOT=yyy

# Charger via python-dotenv
from config.secrets import Secrets
token = Secrets.get_telegram_token()
```

### Validation

```python
# Vérifier les données API
if not data or data.get("status") != "ok":
    logger.error("Erreur API")
    return None

# Vérifier les calculs
if len(candles) < period:
    return None
```

## 📊 Monitoring

### Métriques

```
- Crédits API utilisés/jour
- Nombre de paires alignées
- Nombre de signaux détectés
- Taux de confirmation (bonus)
- Uptime du bot
```

### Heartbeat

```
Toutes les 6 heures:
🤖 Bot actif - 2024-02-24 06:00:00 UTC
```

## 🚀 Déploiement

### Environnement de production

```bash
# Créer un service systemd
[Unit]
Description=Forex Fibonacci Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/fibo_bot
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Logs rotatifs

```
logs/fibo_bot.log (10 MB max)
├─ fibo_bot.log.1
├─ fibo_bot.log.2
├─ fibo_bot.log.3
├─ fibo_bot.log.4
└─ fibo_bot.log.5 (ancien)
```

---

**Version**: 1.0
**Dernière mise à jour**: 2024-02-24
