"""
Módulo responsável pela comunicação com a API do Gemini.
"""
import base64
import hashlib
import json
import os
import tempfile
import time
from typing import List, Optional, Tuple, Dict

import google.generativeai as genai
from PIL import Image
import requests

from config import GEMINI_API_KEY
from utils.cache_manager import CacheManager
from utils.rate_limiter import RateLimiter, ModelType
from utils.image_processor import ImageProcessor
from utils.conversation_history import ConversationHistory

class GeminiClient:
    def __init__(self):
        """Inicializa o cliente da API Gemini."""
        # Configura a biblioteca genai com a chave da API
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Lista os modelos disponíveis
        for m in genai.list_models():
            print(f"Modelo disponível: {m.name}")
        
        # Inicializa os modelos
        self.model_pro = genai.GenerativeModel('gemini-2.5-pro')  # Modelo Pro para texto
        self.model_vision = genai.GenerativeModel('gemini-2.5-flash')  # Modelo 2.5 Flash para imagens
        
        # Inicializa os componentes
        self.cache = CacheManager()
        self.rate_limiter = RateLimiter()
        self.image_processor = ImageProcessor()
        self.history = ConversationHistory()
        
        # Configuração do diretório temporário
        base_temp = tempfile.gettempdir()
        self.temp_dir = os.path.join(base_temp, 'voice_assistant')
        os.makedirs(self.temp_dir, exist_ok=True)

    def _generate_cache_key(self, question: str, image_paths: Optional[List[str]] = None) -> str:
        """
        Gera uma chave única para o cache baseada na pergunta e nas imagens.
        
        Args:
            question: Pergunta do usuário
            image_paths: Lista de caminhos das imagens
            
        Returns:
            str: Chave para o cache
        """
        key_parts = [question]
        
        if image_paths:
            for path in image_paths:
                try:
                    mtime = os.path.getmtime(path)
                    size = os.path.getsize(path)
                    key_parts.append(f"{path}:{mtime}:{size}")
                except OSError:
                    key_parts.append(path)
        
        key_string = "||".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _process_images(self, image_paths: List[str]) -> List[Image.Image]:
        """
        Processa e otimiza as imagens para envio.
        
        Args:
            image_paths: Lista de caminhos das imagens
            
        Returns:
            Lista de imagens processadas
        """
        processed_images = []
        for path in image_paths:
            try:
                image = Image.open(path)
                processed_images.append(image)
            except Exception as e:
                print(f"Erro ao processar imagem {path}: {str(e)}")
        return processed_images

    def _extract_tags(self, text: str) -> List[str]:
        """
        Extrai palavras-chave relevantes do texto para usar como tags.
        
        Args:
            text: Texto para análise
            
        Returns:
            Lista de tags
        """
        stop_words = {'a', 'o', 'e', 'é', 'de', 'do', 'da', 'em', 'para', 'com', 'um', 'uma'}
        
        words = set()
        for word in text.lower().split():
            word = ''.join(c for c in word if c.isalnum())
            if word and len(word) > 3 and word not in stop_words:
                words.add(word)
        
        return list(words)[:5]

    def send_query(self, question: str, image_paths: Optional[List[str]] = None, max_retries: int = 3) -> str:
        """
        Envia uma pergunta e opcionalmente imagens para a API do Gemini.
        
        Args:
            question: Pergunta do usuário
            image_paths: Lista de caminhos das imagens para análise
            max_retries: Número máximo de tentativas em caso de erro
            
        Returns:
            str: Resposta da API do Gemini em português
        """
        # Pesquisa na internet se solicitado explicitamente
        if "pesquise na internet" in question.lower() or "pesquisa na internet" in question.lower():
            try:
                query = question.lower().replace("pesquise na internet", "").replace("pesquisa na internet", "").strip()
                if not query:
                    return "Por favor, especifique o que deseja pesquisar na internet."
                url = f"https://duckduckgo.com/html/?q={query}"
                resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
                if resp.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(resp.text, "html.parser")
                    results = []
                    for r in soup.select(".result__snippet")[:3]:
                        results.append(r.get_text())
                    if results:
                        resposta = "Resultados da pesquisa na internet:\n" + "\n\n".join(results)
                        for char in ['*', '´', '`', '"', "'"]:
                            resposta = resposta.replace(char, "")
                        return resposta
                    else:
                        return "Nenhum resultado relevante encontrado na internet."
                else:
                    return "Não foi possível acessar a pesquisa na internet no momento."
            except Exception as e:
                return f"Erro ao realizar pesquisa na internet: {e}"

        # Verifica cache primeiro
        cache_key = self._generate_cache_key(question, image_paths)
        cached_response = self.cache.get(cache_key)
        if cached_response:
            self.history.add_conversation(
                question=question,
                response=cached_response,
                images=image_paths,
                tags=self._extract_tags(question + " " + cached_response)
            )
            return cached_response

        retries = 0
        last_error = None
        while retries < max_retries:
            try:
                # Aguarda permissão do rate limiter
                if not self.rate_limiter.wait_for_token(timeout=10):
                    wait_times = self.rate_limiter.get_wait_time()
                    wait_msg = [f"{model.value}: {time:.1f}s" for model, time in wait_times.items()]
                    return (f"Serviço temporariamente indisponível. "
                           f"Tempo de espera por modelo: {', '.join(wait_msg)}")

                # Monta o histórico de conversas para contexto
                historico = self.history.get_recent_conversations(5)
                contexto = ""
                for h in historico:
                    contexto += f"Usuário: {h.get('question','')}\nAssistente: {h.get('response','')}\n"
                # Prompt sem cumprimentos e com histórico
                prompt = (
                    "Responda em português do Brasil, de forma clara, objetiva e sem cumprimentos iniciais como 'Olá' ou 'Oi'. "
                    "Considere o contexto da conversa abaixo:\n"
                    f"{contexto}"
                    f"Usuário: {question}\n"
                    "Assistente:"
                )

                # Configura os parâmetros de geração
                generation_config = {
                    "temperature": 0.7,
                    "top_k": 32,
                    "top_p": 1,
                    "max_output_tokens": 2048,
                }

                # Gera a resposta com o modelo apropriado
                if image_paths:
                    processed_images = self._process_images(image_paths)
                    response = self.model_vision.generate_content(
                        [prompt, *processed_images],
                        generation_config=generation_config
                    )
                else:
                    response = self.model_pro.generate_content(
                        prompt,
                        generation_config=generation_config
                    )

                if hasattr(response, "text") and response.text:
                    response_text = response.text

                    # Remove caracteres indesejados: *, ´, `, " e '
                    for char in ['*', '´', '`', '"', "'"]:
                        response_text = response_text.replace(char, "")

                    # Salva no cache
                    self.cache.set(cache_key, response_text)
                    
                    # Adiciona ao histórico
                    self.history.add_conversation(
                        question=question,
                        response=response_text,
                        images=image_paths,
                        tags=self._extract_tags(question + " " + response_text)
                    )
                    
                    # Salva a resposta em JSON
                    self._save_temp_response(response_text)
                    return response_text
                else:
                    # Verifica se foi bloqueado por safety_ratings
                    if hasattr(response, "candidates") and response.candidates:
                        blocked = any(
                            hasattr(c, "safety_ratings") and c.safety_ratings
                            for c in response.candidates
                        )
                        if blocked:
                            return "A resposta foi bloqueada por questões de segurança do modelo Gemini."
                    return "Desculpe, não consegui processar sua pergunta."

            except Exception as e:
                print(f"Erro ao enviar query: {str(e)}")
                retries += 1
                last_error = str(e)
                if retries < max_retries:
                    backoff_time = 2 ** retries
                    print(f"Erro na requisição. Tentativa {retries} de {max_retries}...")
                    time.sleep(backoff_time)
                    continue

        # Se chegou aqui, todas as tentativas falharam
        error_msg = "Desculpe, ocorreu um erro ao processar sua pergunta."
        print(f"Erro final: {last_error}")
        return error_msg

    def _save_temp_response(self, response_text: str, temp_file: Optional[str] = None) -> bool:
        """
        Salva a resposta em um arquivo JSON temporário.
        
        Args:
            response_text: Texto da resposta
            temp_file: Nome do arquivo temporário
            
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        try:
            if temp_file is None:
                temp_file = f'gemini_response_{int(time.time())}.json'
            temp_path = os.path.join(self.temp_dir, temp_file)
            
            response_data = {
                'response': response_text,
                'timestamp': time.time(),
                'model': self.rate_limiter.get_current_model().value,
                'status': 'success'
            }
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, ensure_ascii=False, indent=2)
            return True
            
        except Exception as e:
            print(f"Erro ao salvar resposta temporária: {str(e)}")
            return False

    def get_recent_conversations(self, limit: int = 5) -> List[Dict]:
        """
        Recupera as conversas mais recentes.
        
        Args:
            limit: Número máximo de conversas para retornar
            
        Returns:
            Lista de conversas mais recentes
        """
        return self.history.get_recent_conversations(limit)

    def search_conversations(self, query: str) -> List[Dict]:
        """
        Pesquisa no histórico de conversas.
        
        Args:
            query: Texto para pesquisar
            
        Returns:
            Lista de conversas que correspondem à pesquisa
        """
        return self.history.search_conversations(query)

