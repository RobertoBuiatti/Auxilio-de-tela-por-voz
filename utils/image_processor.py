"""
Módulo responsável pelo processamento e otimização de imagens.
"""
import os
from io import BytesIO
from typing import Optional, Tuple
from PIL import Image

class ImageProcessor:
    def __init__(self):
        """Inicializa o processador de imagens."""
        self.max_size = (1920, 1080)  # Tamanho máximo da imagem
        self.quality = 85  # Qualidade da compressão JPEG
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.webp'}
        
    def optimize_image(self, image_path: str) -> Optional[Tuple[bytes, str]]:
        """
        Otimiza uma imagem para envio à API.
        
        Args:
            image_path: Caminho do arquivo de imagem
            
        Returns:
            Tuple contendo os bytes da imagem otimizada e seu tipo MIME,
            ou None se houver erro
        """
        try:
            # Verifica se o formato é suportado
            file_ext = os.path.splitext(image_path)[1].lower()
            if file_ext not in self.supported_formats:
                print(f"Formato de imagem não suportado: {file_ext}")
                return None

            # Abre e processa a imagem
            with Image.open(image_path) as img:
                # Converte para RGB se necessário
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Redimensiona se maior que o tamanho máximo
                if img.size[0] > self.max_size[0] or img.size[1] > self.max_size[1]:
                    img.thumbnail(self.max_size, Image.Resampling.LANCZOS)
                
                # Salva a imagem otimizada em memória
                output = BytesIO()
                img.save(output, format='JPEG', quality=self.quality, optimize=True)
                
                return output.getvalue(), 'image/jpeg'
                
        except Exception as e:
            print(f"Erro ao processar imagem {image_path}: {str(e)}")
            return None
            
    def get_image_info(self, image_path: str) -> Optional[dict]:
        """
        Obtém informações sobre uma imagem.
        
        Args:
            image_path: Caminho do arquivo de imagem
            
        Returns:
            Dicionário com informações da imagem ou None se houver erro
        """
        try:
            with Image.open(image_path) as img:
                return {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'file_size': os.path.getsize(image_path)
                }
        except Exception as e:
            print(f"Erro ao obter informações da imagem {image_path}: {str(e)}")
            return None
