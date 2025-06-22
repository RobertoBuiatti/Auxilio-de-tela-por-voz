"""
Módulo responsável pelo controle de taxa de requisições.
"""
import time
from collections import deque
from threading import Lock
from typing import Optional, Dict
from enum import Enum
from config import (
    GEMINI_PRO_RPM, GEMINI_PRO_RPD,
    GEMINI_FLASH_RPM, GEMINI_FLASH_RPD
)

class ModelType(Enum):
    """Enum para identificar os modelos disponíveis."""
    PRO = "pro"
    FLASH = "flash"

class ModelLimiter:
    """Controlador de taxa para um modelo específico."""
    def __init__(self, rpm: int, rpd: int):
        """
        Inicializa o controlador para um modelo.
        
        Args:
            rpm: Requisições por minuto permitidas
            rpd: Requisições por dia permitidas
        """
        self.rpm = rpm
        self.rpd = rpd
        self.minute_window = 60  # janela de 1 minuto
        self.day_window = 86400  # janela de 1 dia (24 horas)
        self.minute_requests: deque[float] = deque()
        self.day_requests: deque[float] = deque()
        self._lock = Lock()
        
    def try_acquire(self) -> bool:
        """
        Tenta adquirir uma permissão para fazer uma requisição.
        
        Returns:
            bool: True se a requisição foi permitida, False caso contrário
        """
        with self._lock:
            now = time.time()
            
            # Limpa requisições antigas
            self._clean_old_requests(now)
            
            # Verifica ambos os limites
            if (len(self.minute_requests) < self.rpm and 
                len(self.day_requests) < self.rpd):
                # Adiciona a nova requisição em ambos os controles
                self.minute_requests.append(now)
                self.day_requests.append(now)
                return True
                
            return False
            
    def _clean_old_requests(self, now: float) -> None:
        """
        Remove requisições antigas das filas.
        
        Args:
            now: Timestamp atual
        """
        # Limpa requisições por minuto antigas
        while (self.minute_requests and 
               now - self.minute_requests[0] >= self.minute_window):
            self.minute_requests.popleft()
            
        # Limpa requisições por dia antigas
        while (self.day_requests and 
               now - self.day_requests[0] >= self.day_window):
            self.day_requests.popleft()
            
    def get_wait_time(self) -> float:
        """
        Calcula o tempo estimado de espera para a próxima requisição permitida.
        
        Returns:
            float: Tempo estimado em segundos
        """
        with self._lock:
            now = time.time()
            minute_wait = 0.0
            day_wait = 0.0
            
            if len(self.minute_requests) >= self.rpm:
                minute_wait = max(0.0, self.minute_window - 
                                (now - self.minute_requests[0]))
                
            if len(self.day_requests) >= self.rpd:
                day_wait = max(0.0, self.day_window - 
                             (now - self.day_requests[0]))
                
            return max(minute_wait, day_wait)

class RateLimiter:
    def __init__(self):
        """Inicializa o controlador de taxa de requisições."""
        self.limiters: Dict[ModelType, ModelLimiter] = {
            ModelType.PRO: ModelLimiter(GEMINI_PRO_RPM, GEMINI_PRO_RPD),
            ModelType.FLASH: ModelLimiter(GEMINI_FLASH_RPM, GEMINI_FLASH_RPD)
        }
        self._current_model = ModelType.PRO
        self._lock = Lock()

    def switch_model(self) -> ModelType:
        """
        Alterna entre os modelos disponíveis.
        
        Returns:
            ModelType: O novo modelo selecionado
        """
        with self._lock:
            self._current_model = (ModelType.FLASH if self._current_model == ModelType.PRO 
                                 else ModelType.PRO)
            return self._current_model

    def get_current_model(self) -> ModelType:
        """
        Retorna o modelo atual.
        
        Returns:
            ModelType: O modelo atual
        """
        return self._current_model

    def try_acquire(self) -> bool:
        """
        Tenta adquirir uma permissão para fazer uma requisição.
        
        Returns:
            bool: True se a requisição foi permitida, False caso contrário
        """
        # Tenta primeiro com o modelo atual
        if self.limiters[self._current_model].try_acquire():
            return True
            
        # Se falhar, tenta com o outro modelo
        other_model = ModelType.FLASH if self._current_model == ModelType.PRO else ModelType.PRO
        if self.limiters[other_model].try_acquire():
            self._current_model = other_model
            return True
            
        return False

    def wait_for_token(self, timeout: Optional[float] = None) -> bool:
        """
        Espera até que uma requisição seja permitida ou até atingir o timeout.
        
        Args:
            timeout: Tempo máximo de espera em segundos. None para esperar indefinidamente.
            
        Returns:
            bool: True se conseguiu permissão, False se atingiu o timeout
        """
        start_time = time.time()
        
        while True:
            if self.try_acquire():
                return True
                
            if timeout is not None:
                if time.time() - start_time >= timeout:
                    return False
                    
            time.sleep(0.1)  # Evita consumo excessivo de CPU

    def get_wait_time(self) -> Dict[ModelType, float]:
        """
        Calcula o tempo estimado de espera para cada modelo.
        
        Returns:
            Dict[ModelType, float]: Dicionário com os tempos de espera para cada modelo
        """
        return {
            model: limiter.get_wait_time()
            for model, limiter in self.limiters.items()
        }
