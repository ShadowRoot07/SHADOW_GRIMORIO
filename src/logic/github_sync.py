import os
from pathlib import Path
from loguru import logger

class GitHubSync:
    """Generador de Workflows para delegar poder a la nube."""

    def __init__(self):
        self.workflow_path = Path(".github/workflows")
        # Aseguramos que la carpeta de rituales de nube exista
        self.workflow_path.mkdir(parents=True, exist_ok=True)

    def generar_workflow_compilacion(self, nombre_binario: str):
        """Crea un YAML para compilar C++ en servidores de GitHub."""
        
        yaml_content = f"""name: Compilacion de Alto Rendimiento - {nombre_binario}

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build_native:
    runs-on: ubuntu-latest
    steps:
      - name: Descargando Código del Grimorio
        uses: actions/checkout@v4

      - name: Instalando Compiladores de Élite
        run: sudo apt-get update && sudo apt-get install -y clang make

      - name: Forjando Binario en la Nube
        run: |
          cd core
          make clean
          make
          
      - name: Preservar Artefacto
        uses: actions/upload-artifact@v4
        with:
          name: {nombre_binario}-bin
          path: src/utils/*.so
"""
        
        file_name = f"build_{nombre_binario}.yml"
        full_path = self.workflow_path / file_name
        
        try:
            with open(full_path, "w") as f:
                f.write(yaml_content)
            logger.success(f"📜 [GITHUB_SYNC]: Pergamino '{file_name}' redactado con éxito.")
            return True
        except Exception as e:
            logger.error(f"❌ [GITHUB_SYNC]: Error al escribir el pergamino: {e}")
            return False

# Instancia del Sincronizador
gh_sync = GitHubSync()

