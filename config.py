"""
Módulo de configuração do sistema.
Contém constantes e configurações globais carregadas do arquivo .env
"""
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações da API Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Limites de requisições para cada modelo
GEMINI_PRO_RPM = int(os.getenv('GEMINI_PRO_RPM', '3'))  # Requisições por minuto
GEMINI_PRO_RPD = int(os.getenv('GEMINI_PRO_RPD', '30'))  # Requisições por dia
GEMINI_FLASH_RPM = int(os.getenv('GEMINI_FLASH_RPM', '5'))  # Requisições por minuto
GEMINI_FLASH_RPD = int(os.getenv('GEMINI_FLASH_RPD', '50'))  # Requisições por dia

# Configurações de tokens
MAX_INPUT_TOKENS = int(os.getenv('MAX_INPUT_TOKENS', '1048576').split('#')[0].strip())
MAX_OUTPUT_TOKENS = int(os.getenv('MAX_OUTPUT_TOKENS', '65535').split('#')[0].strip())

# Configurações de áudio
LANGUAGE = os.getenv('LANGUAGE', 'pt-BR')
AUDIO_TIMEOUT = int(os.getenv('AUDIO_TIMEOUT', '10'))
PHRASE_TIMEOUT = int(os.getenv('PHRASE_TIMEOUT', '30'))
MIN_SILENCE_DURATION = float(os.getenv('MIN_SILENCE_DURATION', '1.5'))
SILENCE_THRESHOLD = int(os.getenv('SILENCE_THRESHOLD', '3000'))
DYNAMIC_ENERGY = os.getenv('DYNAMIC_ENERGY', 'True').lower() == 'true'

# Configurações de captura de tela
SCREENSHOT_DIR = os.getenv('SCREENSHOT_DIR', 'screenshots')
SCREENSHOT_FORMAT = os.getenv('SCREENSHOT_FORMAT', 'PNG')
MAX_SCREENSHOTS = int(os.getenv('MAX_SCREENSHOTS', '5'))

# Configurações gerais
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Configurações de Cache
CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', '3600').split('#')[0].strip())  # 1 hora em segundos
MAX_CACHE_ITEMS = int(os.getenv('MAX_CACHE_ITEMS', '100'))

# Validação de configurações críticas
if not GEMINI_API_KEY:
    raise ValueError("A chave da API Gemini não foi configurada no arquivo .env")
