"""
Módulo responsável pela captura e gerenciamento de screenshots.
"""
import os
import time
from datetime import datetime
import pyautogui
from config import SCREENSHOT_DIR, SCREENSHOT_FORMAT

class ScreenshotManager:
    def __init__(self):
        """Inicializa o gerenciador de screenshots."""
        self._setup_directory()
        self.screenshot_paths = []
    
    def _setup_directory(self):
        """Cria o diretório de screenshots se não existir."""
        if not os.path.exists(SCREENSHOT_DIR):
            os.makedirs(SCREENSHOT_DIR)
    
    def _generate_filename(self):
        """Gera um nome único para o arquivo de screenshot."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"screenshot_{timestamp}.{SCREENSHOT_FORMAT.lower()}"
    
    def capture_all_screens(self):
        """Captura screenshots de todas as telas conectadas."""
        self.screenshot_paths = []
        
        try:
            # Captura da tela principal
            main_screen = pyautogui.screenshot()
            filename = self._generate_filename()
            filepath = os.path.join(SCREENSHOT_DIR, filename)
            main_screen.save(filepath)
            self.screenshot_paths.append(filepath)
            
            # Aguarda um breve momento entre capturas
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Erro ao capturar screenshots: {str(e)}")
            return []
        
        return self.screenshot_paths
    
    def clear_screenshots(self):
        """Remove os arquivos de screenshot temporários."""
        for filepath in self.screenshot_paths:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                print(f"Erro ao remover arquivo {filepath}: {str(e)}")
        self.screenshot_paths = []
