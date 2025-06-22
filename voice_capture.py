"""
Módulo responsável pela captura e processamento de áudio.
"""
import os
import time
from config import (
    LANGUAGE, AUDIO_TIMEOUT,
    MIN_SILENCE_DURATION, SILENCE_THRESHOLD,
    PHRASE_TIMEOUT, DYNAMIC_ENERGY
)

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("AVISO: speech_recognition não está instalado. Usando modo de texto.")

class VoiceCapture:
    def __init__(self):
        """Inicializa o sistema de captura de voz."""
        self.is_listening = False
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            # Configurações de sensibilidade do microfone
            self.recognizer.dynamic_energy_threshold = DYNAMIC_ENERGY
            self.recognizer.energy_threshold = SILENCE_THRESHOLD
            # Tempo mínimo de silêncio para considerar fim da frase
            self.recognizer.pause_threshold = MIN_SILENCE_DURATION
            # Tempo máximo para uma única frase
            self.recognizer.phrase_timeout = PHRASE_TIMEOUT
            # Ajuste para não quebrar frases no meio
            self.recognizer.non_speaking_duration = MIN_SILENCE_DURATION
    
    def _is_question(self, text):
        """
        Verifica se o texto contém uma pergunta.
        
        Args:
            text (str): Texto para análise
            
        Returns:
            bool: True se for uma pergunta, False caso contrário
        """
        question_indicators = [
            '?', 'quem', 'qual', 'quais', 'quando', 'onde', 'por que',
            'como', 'o que', 'me diga', 'pode me dizer', 'sabe',
            'explique', 'descreva', 'me fale', 'conte', 'mostre',
            'ajude', 'preciso', 'gostaria'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in question_indicators)
    
    def start_listening(self):
        """Inicia o processo de escuta."""
        self.is_listening = True
        
        if SPEECH_RECOGNITION_AVAILABLE:
            yield from self._voice_mode()
        else:
            yield from self._text_mode()
    
    def _voice_mode(self):
        """Modo de captura por voz usando reconhecimento de fala."""
        print("Iniciando captura de áudio...")
        
        with sr.Microphone() as source:
            print("Ajustando para o ruído ambiente...")
            # Aumenta o tempo de calibração e reduz a sensibilidade inicial
            self.recognizer.adjust_for_ambient_noise(source, duration=3)
            self.recognizer.energy_threshold *= 0.8  # Reduz o threshold para captar melhor
            
            while self.is_listening:
                try:
                    
                    # Coleta o áudio com configurações mais permissivas
                    audio = self.recognizer.listen(
                        source,
                        timeout=AUDIO_TIMEOUT,
                        phrase_time_limit=PHRASE_TIMEOUT,
                        snowboy_configuration=None  # Desativa detecção de palavra-chave
                    )
                    
                    try:
                        text = self.recognizer.recognize_google(
                            audio, 
                            language=LANGUAGE,
                            show_all=False  # Retorna apenas o resultado mais provável
                        )
                        
                        if text and len(text.strip()) > 0:
                            print(f"\nTexto detectado: {text}")
                            print("Processando...")
                            
                            # Se for uma frase longa, considera como pergunta
                            if len(text.split()) >= 3 or self._is_question(text):
                                yield text
                            else:
                                print("Frase muito curta. Continue falando...")
                    
                    except sr.UnknownValueError:
                        print(".", end="", flush=True)  # Indicador de que está ouvindo
                    except sr.RequestError as e:
                        print(f"\nErro na requisição ao serviço de reconhecimento: {str(e)}")
                        time.sleep(1)
                
                except sr.WaitTimeoutError:
                    print(".", end="", flush=True)  # Indicador de que está ouvindo
                except Exception as e:
                    print(f"\nErro durante a captura de áudio: {str(e)}")
                    time.sleep(1)
    
    def _text_mode(self):
        """Modo de entrada por texto quando reconhecimento de voz não está disponível."""
        print("Modo texto ativado - Digite sua pergunta (ou 'sair' para encerrar):")
        
        while self.is_listening:
            try:
                text = input("\n> ").strip()
                if text.lower() == 'sair':
                    break
                    
                if text and len(text.strip()) > 0:
                    is_question = self._is_question(text)
                    if is_question:
                        yield text
                    else:
                        print("Isso não parece ser uma pergunta. Tente novamente.")
                        
            except Exception as e:
                print(f"Erro durante a entrada: {str(e)}")
                continue
    
    def stop_listening(self):
        """Para o processo de escuta."""
        self.is_listening = False
        print("Captura de áudio finalizada.")
