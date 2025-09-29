# React Frontend

Interface légère pour interagir avec l’API FastAPI et tester le modèle DKT.

## Prérequis
- Node.js 18+
- npm ou yarn

## Installation
```bash
cd web_app/frontend
cp .env.example .env           # ajuste VITE_API_URL si besoin
npm install
```

## Lancer le serveur de dev
```bash
npm run dev
```
L’application est disponible sur [http://localhost:5173](http://localhost:5173).

## Fonctionnalités
- Connexion / création de compte (`/auth/register`, `/auth/login`) avec stockage du token Bearer.
- Récupération du bundle d’exercices initial (`/exercises/initial`).
- Soumission des interactions → `POST /interactions` (correction automatique en comparant la réponse à `Exercise.answer`).
- Affichage d’une recommandation (`/recommendations/next`).
- Historique des réponses récentes (`/students/{user}/history`).
- Résumé des probabilités avant/après et tableau de progression par compétence.

## Build de production
```bash
npm run build
npm run preview
```
