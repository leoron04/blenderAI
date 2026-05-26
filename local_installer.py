import os
import subprocess
import shutil
import urllib.request
import urllib.error
import platform
import json

class LocalModelInstaller:
    """Installs and configures a local model (Ollama) based on hardware specs."""

    # Updated database of state-of-the-art models mapped to requirements
    # Organized from most powerful (highest req) to most basic
    MODEL_TIERS = [
        {"id": "llama3.1:70b", "name": "Llama 3.1 70B", "min_vram": 36, "min_ram": 64},
        {"id": "mixtral:8x7b", "name": "Mixtral 8x7B", "min_vram": 24, "min_ram": 32},
        {"id": "qwen2.5:32b", "name": "Qwen 2.5 32B", "min_vram": 16, "min_ram": 24},
        {"id": "llama3.1:8b", "name": "Llama 3.1 8B", "min_vram": 6, "min_ram": 8},
        {"id": "qwen2.5:7b", "name": "Qwen 2.5 7B", "min_vram": 4, "min_ram": 8},
        {"id": "qwen2.5:0.5b", "name": "Qwen 2.5 0.5B", "min_vram": 0, "min_ram": 4} # Fallback for pure CPU or low-end
    ]

    def __init__(self):
        self.os_system = platform.system()
        self.machine = platform.machine()
        self.ram_gb = 0
        self.vram_gb = 0
        self.gpu_vendor = "CPU"
        self.cpu_cores = 1

    def check_hardware(self):
        """Analyzes available RAM, VRAM, and CPU using psutil and system tools."""
        try:
            import psutil
            self.ram_gb = psutil.virtual_memory().total / (1024 ** 3)
            self.cpu_cores = psutil.cpu_count(logical=False) or 1
        except ImportError:
            # Fallback if psutil is not available
            self.ram_gb = 8 # Safe default
            self.cpu_cores = 4

        # Try to check VRAM via nvidia-smi
        try:
            result = subprocess.run(["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                vram_mb = int(result.stdout.strip().split('\n')[0])
                self.vram_gb = vram_mb / 1024
                self.gpu_vendor = "NVIDIA"
        except (FileNotFoundError, ValueError):
            pass

        # Try to check VRAM via rocm if NVIDIA failed
        if self.gpu_vendor == "CPU":
            try:
                result = subprocess.run(["rocminfo"], capture_output=True, text=True)
                if result.returncode == 0:
                    self.gpu_vendor = "AMD"
                    # Very rough estimation or assuming at least 8GB for modern AMD GPUs
                    self.vram_gb = 8
            except FileNotFoundError:
                pass

        # Apple Silicon unified memory
        if self.os_system == "Darwin" and self.machine == "arm64":
            self.gpu_vendor = "Apple"
            self.vram_gb = self.ram_gb * 0.7  # Mac shares RAM as VRAM

        return {
            "RAM": self.ram_gb,
            "VRAM": self.vram_gb,
            "GPU": self.gpu_vendor,
            "Cores": self.cpu_cores,
            "OS": self.os_system
        }

    def suggest_model(self):
        """Suggests the best local model based on hardware specs."""
        if self.ram_gb == 0 and self.vram_gb == 0:
            self.check_hardware()

        for tier in self.MODEL_TIERS:
            # Check if hardware meets the requirements
            if self.vram_gb >= tier["min_vram"] and self.ram_gb >= tier["min_ram"]:
                return tier["id"]

        # Absolute fallback
        return self.MODEL_TIERS[-1]["id"]

    def _is_ollama_running(self):
        """Checks if the Ollama service is currently reachable."""
        try:
            req = urllib.request.Request("http://localhost:11434/")
            urllib.request.urlopen(req, timeout=2)
            return True
        except (urllib.error.URLError, ConnectionRefusedError):
            return False

    def _get_installed_models(self):
        """Retrieves a list of currently installed models in Ollama."""
        if not self._is_ollama_running():
            return []

        try:
            req = urllib.request.Request("http://localhost:11434/api/tags")
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                return [m.get("name") for m in data.get("models", [])]
        except Exception:
            return []

    def install_ollama_and_model(self, report_callback=None):
        """Downloads/Starts Ollama and pulls the suggested model. Handles auto-config."""
        def log(msg):
            if report_callback:
                report_callback(msg)
            print(f"[LocalInstaller] {msg}")

        target_model = self.suggest_model()

        # 1. Check if Ollama is installed
        ollama_path = shutil.which("ollama")
        if not ollama_path:
            log("Ollama non trovato. Per favore installa Ollama dal sito ufficiale: https://ollama.com/download")
            return False, f"Installazione manuale richiesta per Ollama. Modello suggerito per il tuo hardware: {target_model}"

        # 2. Check if Ollama service is running
        if not self._is_ollama_running():
            log("Ollama non in esecuzione. Avvio del servizio Ollama in background...")
            if self.os_system == "Windows":
                subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            import time
            time.sleep(3) # Wait for startup

        # 3. Intelligent auto-config check
        installed_models = self._get_installed_models()

        # Remove version tags for loose matching
        installed_bases = [m.split(":")[0] for m in installed_models]
        target_base = target_model.split(":")[0]

        if target_model in installed_models:
            log(f"Il modello ideale ({target_model}) è già installato. Auto-configurazione completata.")
            return True, target_model

        if target_base in installed_bases:
            # We have a version of this model already (e.g. they have llama3, we suggested llama3.1)
            # Find exact installed string to use
            existing = next(m for m in installed_models if m.startswith(target_base))
            log(f"Versione simile trovata ({existing}). Potresti voler fare l'upgrade a {target_model}.")
            # Fallback to pull the exact requested updated one anyway

        # 4. Pull the model
        log(f"Scaricamento del modello {target_model} in corso (potrebbe richiedere molto tempo e svariati GB)...")
        try:
            subprocess.run(["ollama", "pull", target_model], check=True)
            log(f"Modello {target_model} installato con successo!")
            return True, target_model
        except subprocess.CalledProcessError as e:
            log(f"Errore durante il download del modello: {e}")
            return False, str(e)
