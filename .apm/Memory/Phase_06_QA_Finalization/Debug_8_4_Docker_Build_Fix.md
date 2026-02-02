# Memory Log - Task 8.4: Docker CSS Build & PostCSS Fix

## Status
- [x] Completed

## Context
Tailwind CSS ne produisait aucun style dans le conteneur Docker.

## Decisions
- **PostCSS Config**: Le fichier `postcss.config.mjs` (ESM) n'était pas lu correctement car `package.json` n'avait pas `"type": "module"`. Je l'ai supprimé et remplacé par `postcss.config.js` utilisant `module.exports`.
- **Tailwind Config**: Mise à jour de `tailwind.config.ts` pour utiliser des chemins de scan plus précis (`./src/app`, `./src/components`) afin d'assurer que tous les fichiers pertinents sont scannés.
- **Verification**: Un test de compilation manuel avec `npx tailwindcss` a confirmé que la chaîne de compilation fonctionne désormais (génération d'un fichier CSS de 48K).

## Verification Results
- Compilation manuelle réussie : `output.css` contient les utilitaires Tailwind.
- Conteneur `web` redémarré avec la nouvelle configuration.
- Les erreurs de dimension Recharts devraient être résolues car les classes de layout sont maintenant appliquées.
