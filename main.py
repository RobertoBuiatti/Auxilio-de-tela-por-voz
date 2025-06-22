"""
Módulo principal que orquestra a captura de voz, screenshots e interação com o Gemini.
"""
import signal
import sys
import threading
import time
from voice_capture import VoiceCapture
from screenshot import ScreenshotManager
from gemini_client import GeminiClient
from gtts import gTTS
from playsound import playsound
import os

class VoiceAssistant:
    def __init__(self):
        """Inicializa o assistente de voz."""
        self.voice_capture = VoiceCapture()
        self.screenshot_manager = ScreenshotManager()
        self.gemini_client = GeminiClient()
        # self.speaker = GTTSSpeaker()
        self.running = False
        
        # Configura o tratamento de sinais para encerramento gracioso
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Manipula sinais de interrupção do sistema."""
        print("\nEncerrando o assistente...")
        self.stop()
        sys.exit(0)
    
    def _process_question(self, question):
        """
        Processa uma pergunta detectada.
        
        Args:
            question (str): Pergunta do usuário
        """
        try:
            
            # Captura screenshots em thread separada
            screenshot_thread = threading.Thread(
                target=self._capture_screenshots_async
            )
            screenshot_thread.start()
            
            # Aguarda no máximo 2 segundos pelos screenshots
            screenshot_thread.join(timeout=2)
            screenshot_paths = self.screenshot_manager.screenshot_paths
            
            if not screenshot_paths:
                print("Não foi possível capturar as imagens.")
                return
            
            # Envia a pergunta e as imagens para o Gemini
            response = self.gemini_client.send_query(question, screenshot_paths)
            
            # Limpa os screenshots
            self.screenshot_manager.clear_screenshots()
            
            # Exibe e fala a resposta
            print(response)
            
            # Fala a resposta diretamente
            falar(response)
            
            # Pronto para próxima pergunta imediatamente, sem mensagens intermediárias
            
        except Exception as e:
            print(f"Erro ao processar pergunta: {str(e)}")
    
    def _capture_screenshots_async(self):
        """Captura screenshots em uma thread separada."""
        self.screenshot_manager.capture_all_screens()
    
    def start(self):
        """Inicia o assistente de voz."""
        try:
            self.running = True
            # Inicia a captura de voz sem cumprimentos
            for question in self.voice_capture.start_listening():
                if not self.running:
                    break

                # Processa a pergunta em um thread separado
                process_thread = threading.Thread(
                    target=self._process_question,
                    args=(question,)
                )
                process_thread.daemon = True
                process_thread.start()
        except Exception as e:
            print(f"Erro ao iniciar o assistente: {str(e)}")
            self.stop()
    
    def stop(self):
        """Para o assistente de voz e limpa histórico e áudios."""
        self.running = False
        # self.speaker.stop()
        self.voice_capture.stop_listening()

        # Remove histórico de conversas
        try:
            if os.path.exists("conversation_history.db"):
                os.remove("conversation_history.db")
        except Exception as e:
            print(f"Erro ao remover histórico de conversas: {e}")

        # Remove áudios temporários do Gemini
        try:
            temp_dir = getattr(self.gemini_client, "temp_dir", None)
            if temp_dir and os.path.exists(temp_dir):
                for f in os.listdir(temp_dir):
                    try:
                        os.remove(os.path.join(temp_dir, f))
                    except Exception as e:
                        print(f"Erro ao remover arquivo de áudio: {e}")
        except Exception as e:
            print(f"Erro ao limpar áudios temporários: {e}")

        # Remove resposta_gemini.mp3 se existir
        try:
            if os.path.exists("resposta_gemini.mp3"):
                os.remove("resposta_gemini.mp3")
        except Exception as e:
            print(f"Erro ao remover resposta_gemini.mp3: {e}")

        print("Assistente finalizado. Histórico e áudios removidos.")

def falar(texto):
    """Converte texto em fala usando gTTS e playsound."""
    if not texto:
        return
    try:
        tts = gTTS(text=texto, lang='pt')
        filename = "resposta_gemini.mp3"
        tts.save(filename)
        playsound(filename)
        os.remove(filename)
    except Exception as e:
        print(f"Erro ao gerar ou reproduzir o áudio: {e}")

def main():
    """Função principal."""
    assistant = VoiceAssistant()
    assistant.start()

if __name__ == "__main__":
    main()
