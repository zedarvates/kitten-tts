#!/usr/bin/env python3
"""Kitten TTS — Local real-time text-to-speech bridge for Hermes Agent.

Converts Hermes text responses to speech using Piper TTS (local, fast).
Delivers audio via Telegram, Discord, CLI, or direct playback.

Usage modes:
  say "Bonjour"           → Play locally
  say --telegram "Salut"  → Send voice to Telegram
  say --stream            → Real-time sentence-by-sentence
  kitten-server           → HTTP API on port 8766

Dependencies: piper-tts, edge-tts (fallback)
"""

import subprocess, sys, os, json, tempfile, time, shutil
from pathlib import Path
from dataclasses import dataclass

HOME = Path.home()
AUDIO_CACHE = HOME / ".hermes" / "audio_cache"
PIPER_MODEL = HOME / ".local" / "share" / "piper-tts" / "fr_FR-siwis-medium.onnx"
PIPER_CONFIG = str(PIPER_MODEL) + ".json"
PIPER_BIN = shutil.which("piper") or str(HOME / ".local" / "bin" / "piper")

# Fallback: Edge TTS (free Microsoft voices, used if Piper fails)
EDGE_TTS = shutil.which("edge-tts")

# Voice personality
VOICE = {
    "length_scale": "1.1",    # Slightly slower, clearer
    "noise_scale": "0.5",     # Cleaner sound
    "noise_w": "0.45",
    "sentence_silence": "0.3", # 300ms between sentences
}

@dataclass
class Kitten:
    """Kitten TTS engine."""
    
    def say(self, text: str, output: str = None) -> str:
        """Convert text to speech, return path to WAV file."""
        if not output:
            AUDIO_CACHE.mkdir(parents=True, exist_ok=True)
            output = str(AUDIO_CACHE / f"kitten_{int(time.time())}.wav")
        
        if PIPER_BIN and PIPER_MODEL.exists():
            return self._piper_tts(text, output)
        elif EDGE_TTS:
            return self._edge_tts(text, output)
        else:
            raise RuntimeError("No TTS engine available (install piper-tts or edge-tts)")
    
    def _piper_tts(self, text: str, output: str) -> str:
        """Use Piper TTS (local, offline, fast)."""
        cmd = [
            PIPER_BIN,
            "-m", str(PIPER_MODEL),
            "--output_file", output,
            "--length_scale", VOICE["length_scale"],
            "--noise_scale", VOICE["noise_scale"],
            "--noise_w", VOICE["noise_w"],
            "--sentence_silence", VOICE["sentence_silence"],
        ]
        proc = subprocess.run(
            cmd,
            input=text.encode(),
            capture_output=True,
            timeout=30,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Piper failed: {proc.stderr.decode()}")
        
        # Convert WAV to OGG (Telegram prefers OGG/OPUS)
        ogg_output = output.replace(".wav", ".ogg")
        subprocess.run([
            "ffmpeg", "-y", "-i", output,
            "-c:a", "libopus", "-b:a", "24k",
            ogg_output
        ], capture_output=True)
        
        if os.path.exists(ogg_output):
            return ogg_output
        return output
    
    def _edge_tts(self, text: str, output: str) -> str:
        """Fallback: Edge TTS (free, cloud, French voice)."""
        mp3_output = output.replace(".wav", ".mp3")
        subprocess.run([
            EDGE_TTS,
            "--voice", "fr-FR-DeniseNeural",
            "--text", text,
            "--write-media", mp3_output,
        ], capture_output=True, timeout=30)
        return mp3_output
    
    def stream_say(self, text: str) -> list[str]:
        """Split text into sentences, generate audio for each.
        Returns list of audio file paths for real-time streaming.
        """
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        files = []
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                f = self.say(sentence.strip())
                files.append(f)
        return files


def main():
    if len(sys.argv) < 2:
        print("Kitten TTS — Hermes voice engine")
        print("Usage: kitten say 'text' | kitten --telegram 'text' | kitten server")
        print(f"Model: {PIPER_MODEL.name}")
        print(f"Engine: {'Piper (local)' if PIPER_MODEL.exists() else 'Edge TTS (cloud)'}")
        return
    
    kitten = Kitten()
    cmd = sys.argv[1]
    
    if cmd == "say":
        text = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read()
        output = kitten.say(text)
        print(f"MEDIA:{output}")
    
    elif cmd == "--telegram":
        text = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read()
        output = kitten.say(text)
        # Hermes will auto-deliver MEDIA: paths via gateway
        print(f"MEDIA:{output}")
    
    elif cmd == "stream":
        text = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read()
        files = kitten.stream_say(text)
        for f in files:
            print(f"MEDIA:{f}")
    
    elif cmd == "server":
        from http.server import HTTPServer, BaseHTTPRequestHandler
        class TTSHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get('Content-Length', 0))
                text = self.rfile.read(length).decode()
                try:
                    output = kitten.say(text)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"path": output}).encode())
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
            def do_GET(self):
                if self.path == "/health":
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'{"status":"ok","engine":"piper"}')
        server = HTTPServer(('127.0.0.1', 8766), TTSHandler)
        print("🐱 Kitten TTS server on http://127.0.0.1:8766")
        server.serve_forever()
    
    elif cmd == "test":
        kitten.say("Bonjour, je suis Hermes. Je parle français maintenant.")
        print("✅ Test réussi — écoute l'audio dans", AUDIO_CACHE)
    
    elif cmd == "install":
        print("📦 Installation Kitten TTS...")
        if not PIPER_MODEL.exists():
            print("Téléchargement du modèle français...")
            os.system(f"wget -q -P {PIPER_MODEL.parent} https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx")
            os.system(f"wget -q -P {PIPER_MODEL.parent} https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json")
        print("✅ Kitten TTS prêt !")


if __name__ == "__main__":
    main()
