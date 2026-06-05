# Kitten TTS API Reference

Base URL: `http://localhost:8767`

## Endpoints

### `POST /tts` — Synthèse vocale

Synthétise un texte en audio.

**Requête :**
```json
{
  "text": "Bonjour, je suis Hermes",
  "voice": "fr_FR-siwis-medium",
  "format": "ogg"
}
```

**Réponse :**
- `200 OK` — Flux audio OGG/WAV/MP3 (Content-Type: `audio/ogg`)
- `400 Bad Request` — Texte manquant ou trop long
- `500 Internal Server Error` — Erreur de synthèse

### `GET /health` — Statut du service

**Réponse :**
```json
{
  "status": "ok",
  "model": "fr_FR-siwis-medium",
  "uptime": 3600,
  "version": "1.0.0"
}
```

## Formats supportés

| Format | Content-Type | Usage |
|--------|-------------|-------|
| `ogg` | `audio/ogg` | Telegram, Discord (recommandé) |
| `wav` | `audio/wav` | Haute qualité, debug |
| `mp3` | `audio/mpeg` | Compatibilité maximale |

## Exemples

### curl
```bash
curl -X POST http://localhost:8767/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Bonjour, je suis Hermes"}' \
  --output bonjour.ogg
```

### Python
```python
import requests

r = requests.post("http://localhost:8767/tts", json={
    "text": "Bonjour, je suis Hermes",
    "voice": "fr_FR-siwis-medium"
})
with open("bonjour.ogg", "wb") as f:
    f.write(r.content)
```

### JavaScript
```javascript
const response = await fetch("http://localhost:8767/tts", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ text: "Bonjour, je suis Hermes" })
});
const blob = await response.blob();
// Utiliser blob dans Audio/HTML
```

### Hermes (MCP)
```
Tool: mcp_localai_localai_tts
Paramètres: text="Bonjour", voice="fr_FR-siwis-medium"
```

## Limites

- Texte max: 2000 caractères par requête
- Débit: ~100ms par phrase
- Modèle: 60MB RAM
- CPU only (pas de GPU nécessaire)
