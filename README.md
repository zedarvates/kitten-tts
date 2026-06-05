# Kitten TTS 🐱

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)]()

Text-to-Speech local ultra-rapide pour Hermes Agent — 100% français, 100% CPU, ~100ms par phrase.

Téléphone, Telegram, Discord, CLI, API HTTP. Zéro cloud, zéro latence réseau.

## Pourquoi Kitten ?

- **100% local** — Piper TTS sur CPU, pas de cloud, pas de latence réseau
- **Français natif** — Voix `fr_FR-siwis-medium`, claire et naturelle
- **Temps réel** — ~100ms par phrase, streaming possible
- **Multi-canal** — Telegram, Discord, CLI, API HTTP, MCP
- **Léger** — 60MB le modèle, ~10KB par message audio (OGG Opus)
- **MCP intégré** — Tool MCP `mcp_localai_localai_tts` disponible dans Hermes

## Usage

```bash
# Parler directement (CLI)
kitten "Bonjour, je suis Hermes"

# Via pipe
echo "Il est 14h, tout va bien" | kitten

# Streaming phrase par phrase
python3 kitten_tts.py stream "Phrase 1. Phrase 2. Phrase 3."

# Serveur HTTP (port 8767)
python3 kitten_tts.py server
```

## API HTTP

Le serveur écoute sur `http://localhost:8767`.

### Synthèse vocale
```
POST /tts
Content-Type: application/json

{"text": "Bonjour, je suis Hermes", "voice": "fr_FR-siwis-medium"}

→ 200 OK
Content-Type: audio/ogg
(body: flux audio OGG Opus)
```

### Statut
```
GET /health

→ 200 OK
{"status": "ok", "model": "fr_FR-siwis-medium", "uptime": 3600}
```

### Paramètres
| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `text` | string | requis | Texte à synthétiser (max 2000 chars) |
| `voice` | string | `fr_FR-siwis-medium` | Voix Piper (voir liste ci-dessous) |
| `format` | string | `ogg` | Format audio: `ogg`, `wav`, `mp3` |

### Voix disponibles
- `fr_FR-siwis-medium` — Voix française claire et naturelle (recommandée)
- `serena` — Voix Qwen3 alternative

## Intégration Hermes

### Via MCP (recommandé)
```bash
# Dans Hermes, utilise le tool MCP natif :
mcp_localai_localai_tts(text="Bonjour", voice="fr_FR-siwis-medium")
```

### Via le skill Hermes
Le skill `kitten-tts` est installé dans Hermes :
```
~/.hermes/skills/media/kitten-tts/SKILL.md
```

### Via text_to_speech tool
```bash
# Hermes dispose d'un tool text_to_speech intégré
# Configure dans hermes config → TTS → provider: localai
```

## Architecture

```
Hermes Agent
  └─> text_to_speech() / MCP tool
       └─> kitten_tts.py (port :8767)
            ├─ Piper TTS (local, CPU, 60MB)
            │   └─ WAV → OGG Opus (ffmpeg)
            └─ MCP bridge → Hermes Gateway
                 └─ Telegram / Discord / CLI
```

## Installation

```bash
# Installer Piper TTS
pip install piper-tts

# Installer le modèle français
python3 kitten_tts.py install

# Rendre la CLI accessible
chmod +x ~/.local/bin/kitten

# Démarrer le serveur
python3 kitten_tts.py server &

# Tester
curl -X POST http://localhost:8767/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Bonjour, je suis Hermes"}' \
  --output test.ogg
```

## Intégration Hermes (config)

```yaml
# ~/.hermes/config.yaml (extrait)
tools:
  tts:
    provider: localai
    endpoint: http://localhost:8767/tts
    voice: fr_FR-siwis-medium
```

## Dépendances

- Python 3.10+
- `piper-tts` (moteur TTS)
- `ffmpeg` (conversion audio)
- `flask` ou `fastapi` (serveur HTTP) — optionnel

## Projets liés

- [hermes-agent](https://github.com/zedarvates/hermes-agent) — Agent Hermes principal
- [hnoss-voice](https://github.com/zedarvates/hnoss-voice) — Assistant vocal always-on
- [hermes-brain](https://github.com/zedarvates/hermes-brain) — Architecture cognitive

## Licence

MIT
