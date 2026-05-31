# Kitten TTS 🐱

Text-to-Speech local ultra-rapide pour Hermes Agent.
Te permet de parler en français directement via Telegram, Discord, et CLI.

## Pourquoi Kitten ?

- **100% local** — Piper TTS sur CPU, pas de cloud, pas de latence réseau
- **Français natif** — Voix `siwis-medium`, claire et naturelle
- **Temps réel** — ~100ms par phrase, streaming possible
- **Multi-canal** — Telegram, Discord, CLI, API HTTP
- **Léger** — 60MB le modèle, ~10KB par message audio (OGG Opus)

## Usage

```bash
# Parler directement
kitten "Bonjour, je suis Hermes"

# Via pipe
echo "Il est 14h, tout va bien" | kitten

# Streaming phrase par phrase
python3 kitten_tts.py stream "Phrase 1. Phrase 2. Phrase 3."

# Serveur HTTP (port 8766)
python3 kitten_tts.py server
```

## Architecture

```
Hermes Agent
  └─> text_to_speech() 
       └─> kitten_tts.py
            ├─ Piper TTS (local, CPU, 60MB)
            │   └─ WAV → OGG Opus (ffmpeg)
            └─ Edge TTS (cloud, fallback)
            └─ MEDIA:path → Gateway (Telegram/Discord)
```

## Installation

```bash
pip install piper-tts
python3 kitten_tts.py install
chmod +x ~/.local/bin/kitten
```

## Intégration Hermes

Le skill `kitten-tts` charge automatiquement Kitten dans Hermes.
Pour parler : `text_to_speech("Ton message")`

---

## 🤝 Support

If you find this project useful, consider supporting its development:

| Coin | Address |
|------|---------|
| ₿ **Bitcoin** | `bc1qcqhgfyay56dqexrrnvzguqdczxct0vykqz38dz` |
| Ξ **Ethereum** | `0x1CbE662f1d6C58bc2adEE57F0e17216882BAc36c` |

Your support helps keep the servers running ☕
