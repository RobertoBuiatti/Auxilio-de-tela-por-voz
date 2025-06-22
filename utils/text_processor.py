"""
Módulo responsável pelo processamento e formatação de texto antes da sintetização.
"""
import re
from typing import Dict, List, Optional

class TextProcessor:
    def __init__(self):
        """Inicializa o processador de texto."""
        # Mapeamento de caracteres especiais para suas versões faladas
        self.special_chars: Dict[str, str] = {
            '%': ' por cento',
            '$': ' reais',
            '€': ' euros',
            '£': ' libras',
            '@': ' arroba',
            '#': ' hashtag',
            '&': ' e',
            '+': ' mais',
            '=': ' igual a',
            '<': ' menor que',
            '>': ' maior que',
            '™': '',
            '®': '',
            '©': '',
            '°': ' graus',
        }
        
        # Abreviações comuns
        self.abbreviations: Dict[str, str] = {
            'dr.': 'doutor',
            'dra.': 'doutora',
            'sr.': 'senhor',
            'sra.': 'senhora',
            'prof.': 'professor',
            'profa.': 'professora',
            'eng.': 'engenheiro',
            'etc.': 'etcétera',
            'ex.': 'exemplo',
            'tel.': 'telefone',
            'cel.': 'celular',
            'av.': 'avenida',
            'hrs.': 'horas',
            'min.': 'minutos',
            'seg.': 'segundos',
        }

    def format_numbers(self, text: str) -> str:
        """
        Formata números para serem lidos corretamente.
        
        Args:
            text: Texto a ser processado
            
        Returns:
            Texto com números formatados
        """
        # Converte números para extenso em casos específicos
        def format_number(match):
            num = match.group(0)
            if '.' in num:
                # Trata números decimais
                parts = num.split('.')
                if len(parts[1]) == 1:
                    parts[1] += '0'
                return f"{parts[0]} vírgula {parts[1]}"
            return num
            
        # Procura números no texto
        text = re.sub(r'\d+\.\d+', format_number, text)
        
        # Formata datas (DD/MM/YYYY)
        text = re.sub(
            r'(\d{2})/(\d{2})/(\d{4})',
            lambda m: f"{m.group(1)} de {m.group(2)} de {m.group(3)}",
            text
        )
        
        return text

    def format_urls(self, text: str) -> str:
        """
        Formata URLs para serem lidas de forma mais natural.
        
        Args:
            text: Texto a ser processado
            
        Returns:
            Texto com URLs formatadas
        """
        # Substitui www. por "www ponto"
        text = re.sub(r'www\.', 'www ponto ', text)
        
        # Substitui .com por "ponto com"
        text = re.sub(r'\.com', ' ponto com', text)
        
        # Substitui outros domínios comuns
        text = re.sub(r'\.org', ' ponto org', text)
        text = re.sub(r'\.gov', ' ponto gov', text)
        text = re.sub(r'\.edu', ' ponto edu', text)
        text = re.sub(r'\.br', ' ponto br', text)
        
        # Substitui // por "barra barra"
        text = re.sub(r'//', ' barra barra ', text)
        
        return text

    def format_special_chars(self, text: str) -> str:
        """
        Substitui caracteres especiais por suas versões faladas.
        
        Args:
            text: Texto a ser processado
            
        Returns:
            Texto com caracteres especiais substituídos
        """
        for char, replacement in self.special_chars.items():
            text = text.replace(char, replacement)
        return text

    def expand_abbreviations(self, text: str) -> str:
        """
        Expande abreviações comuns.
        
        Args:
            text: Texto a ser processado
            
        Returns:
            Texto com abreviações expandidas
        """
        words = text.split()
        for i, word in enumerate(words):
            word_lower = word.lower()
            if word_lower in self.abbreviations:
                words[i] = self.abbreviations[word_lower]
        return ' '.join(words)

    def clean_text(self, text: str) -> str:
        """
        Remove caracteres indesejados e formata o texto.
        
        Args:
            text: Texto a ser processado
            
        Returns:
            Texto limpo e formatado
        """
        # Remove múltiplos espaços
        text = re.sub(r'\s+', ' ', text)
        
        # Remove caracteres de controle
        text = ''.join(char for char in text if char >= ' ')
        
        # Remove emojis
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        return text.strip()

    def format_for_speech(self, text: str) -> str:
        """
        Aplica todas as formatações necessárias para sintetização.
        
        Args:
            text: Texto a ser processado
            
        Returns:
            Texto formatado para sintetização
        """
        text = self.clean_text(text)
        text = self.format_special_chars(text)
        text = self.format_numbers(text)
        text = self.format_urls(text)
        text = self.expand_abbreviations(text)
        
        # Adiciona pausas em pontuações
        text = re.sub(r'([.!?;])', r'\1, ', text)
        
        return text
