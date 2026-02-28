# 🚀 Déploiement GitHub - Forex Fibonacci Bot

## Étape 1: Extraire et Préparer

```bash
unzip fibo_bot.zip
cd fibo_bot
```

## Étape 2: Créer Repo GitHub

```bash
git init
git add .
git commit -m "Initial commit: Forex Fibonacci Bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/fibo_bot.git
git push -u origin main
```

## Étape 3: Configurer les Secrets GitHub

1. Aller sur : `https://github.com/YOUR_USERNAME/fibo_bot/settings/secrets/actions`
2. Ajouter 2 secrets :
   - `TELEGRAM_TOKEN_FIBOBOT` = `8605370883:AAH4XVlq3lYVJzmAB9v3OC7J8x_6KLR4klw`
   - `TWELVEDATA_API_KEY_FIBOBOT` = `9d61193621de4d7f976f78147fa689b1`

## Étape 4: Déployer sur Render/Railway/Heroku

### Option A: Render (Recommandé)

1. Aller sur https://render.com
2. Créer nouveau "Web Service"
3. Connecter le repo GitHub
4. Paramètres:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python main.py`
5. Ajouter variables d'environnement (depuis GitHub Secrets)
6. Deploy

### Option B: Railway

1. Aller sur https://railway.app
2. Créer nouveau projet
3. Connecter GitHub
4. Ajouter variables d'environnement
5. Deploy automatique

### Option C: Heroku

1. Installer Heroku CLI
2. `heroku login`
3. `heroku create fibo-bot`
4. `heroku config:set TELEGRAM_TOKEN_FIBOBOT=...`
5. `heroku config:set TWELVEDATA_API_KEY_FIBOBOT=...`
6. `git push heroku main`

## Étape 5: Vérifier le Déploiement

```bash
# Voir les logs
heroku logs --tail
# ou
railway logs
# ou
render logs
```

## Étape 6: Tester le Bot

Envoyer `/start` au bot Telegram

## 🔑 Variables d'Environnement Requises

```
TELEGRAM_TOKEN_FIBOBOT=8605370883:AAH4XVlq3lYVJzmAB9v3OC7J8x_6KLR4klw
TWELVEDATA_API_KEY_FIBOBOT=9d61193621de4d7f976f78147fa689b1
LOG_LEVEL=INFO
```

## 📊 Ressources Requises

- RAM: 256MB minimum
- CPU: Partagé OK
- Disque: 100MB
- Uptime: 24/7 recommandé

## 🛑 Arrêter le Bot

```bash
# Render/Railway/Heroku
# Aller dans le dashboard et cliquer "Stop"

# Ou via CLI:
heroku ps:stop worker
```

## 📝 Notes

- Le bot utilise **4 Fibonacci multi-niveaux**
- Crédits API: 800/jour (Twelve Data)
- Rate limiting: 8 req/min
- Base de données: SQLite (locale)
- Logs: Rotatifs (max 10MB)

## ✅ Checklist Déploiement

- [ ] Repo GitHub créé
- [ ] Secrets configurés
- [ ] Plateforme choisie (Render/Railway/Heroku)
- [ ] Variables d'environnement ajoutées
- [ ] Bot déployé
- [ ] Logs vérifiés
- [ ] `/start` testé sur Telegram
- [ ] Premiers signaux reçus

---

**Le bot est prêt à trader en production! 🚀**
