"""
Módulo responsável pelo gerenciamento de cache em memória.
"""
import time
from collections import OrderedDict
from typing import Any, Optional
from config import CACHE_ENABLED, CACHE_TIMEOUT, MAX_CACHE_ITEMS

class CacheManager:
    def __init__(self):
        """Inicializa o gerenciador de cache."""
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self.enabled = CACHE_ENABLED
        self.timeout = CACHE_TIMEOUT
        self.max_items = MAX_CACHE_ITEMS

    def get(self, key: str) -> Optional[Any]:
        """
        Recupera um item do cache se ele existir e não estiver expirado.
        
        Args:
            key: Chave do item no cache
            
        Returns:
            O valor armazenado ou None se não encontrado/expirado
        """
        if not self.enabled:
            return None

        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp <= self.timeout:
                # Move item para o final (mais recente)
                self._cache.move_to_end(key)
                return value
            else:
                # Remove item expirado
                del self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """
        Armazena um item no cache.
        
        Args:
            key: Chave para armazenar o valor
            value: Valor a ser armazenado
        """
        if not self.enabled:
            return

        # Remove itens mais antigos se exceder o limite
        while len(self._cache) >= self.max_items:
            self._cache.popitem(last=False)

        self._cache[key] = (value, time.time())
        self._cache.move_to_end(key)

    def clear(self) -> None:
        """Limpa todo o cache."""
        self._cache.clear()

    def remove(self, key: str) -> None:
        """
        Remove um item específico do cache.
        
        Args:
            key: Chave do item a ser removido
        """
        if key in self._cache:
            del self._cache[key]
