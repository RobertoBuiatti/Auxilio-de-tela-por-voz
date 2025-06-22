# Assistente de Voz com Análise de Imagens

Sistema de assistente de voz que utiliza a API Gemini para análise de imagens e geração de respostas em português.

## Funcionalidades

- Captura de voz em português do Brasil
- Captura de tela automática
- Análise de imagens via API Gemini
- Resposta em áudio usando síntese de voz
- Cache de respostas para melhor performance
- Rate limiting para controle de requisições
- Otimização automática de imagens
- Gestão segura de configurações via variáveis de ambiente

## Requisitos

- Python 3.8+
- Bibliotecas listadas em `requirements.txt`
- Chave de API do Google Gemini

## Instalação

1. Clone o repositório
```bash
git clone https://seu-repositorio.git
cd seu-repositorio
```

2. Crie um ambiente virtual e ative-o
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instale as dependências
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente
```bash
# Copie o arquivo de exemplo
cp .env.example .env
# Edite o arquivo .env e adicione sua chave da API Gemini
```

## Configuração

O arquivo `.env` contém todas as configurações necessárias:

- `GEMINI_API_KEY`: Sua chave de API do Google Gemini
- `LANGUAGE`: Idioma para reconhecimento de voz (padrão: pt-BR)
- `AUDIO_TIMEOUT`: Tempo máximo de espera por áudio em segundos
- `SCREENSHOT_DIR`: Diretório para salvar capturas de tela
- `MAX_SCREENSHOTS`: Número máximo de screenshots por requisição
- `CACHE_ENABLED`: Habilita/desabilita o cache de respostas
- `CACHE_TIMEOUT`: Tempo de expiração do cache em segundos
- `MAX_CACHE_ITEMS`: Número máximo de itens no cache
- `MAX_REQUESTS_PER_MINUTE`: Limite de requisições por minuto

## Uso

1. Inicie o assistente:
```bash
python main.py
```

2. Fale sua pergunta quando solicitado

3. O sistema irá:
   - Capturar sua voz
   - Tirar screenshots da tela
   - Analisar as imagens
   - Gerar uma resposta em português
   - Reproduzir a resposta em áudio

## Performance

O sistema inclui várias otimizações para melhor desempenho:

- **Cache**: Respostas são armazenadas em cache para perguntas repetidas
- **Rate Limiting**: Controle automático de taxa de requisições
- **Otimização de Imagens**: 
  - Redimensionamento automático
  - Compressão inteligente
  - Conversão de formato
- **Backoff Exponencial**: Retry automático em caso de falhas
- **Gerenciamento de Memória**: Limpeza automática de arquivos temporários

## Estrutura do Projeto

```
.
├── main.py              # Ponto de entrada
├── config.py            # Configurações
├── gemini_client.py     # Cliente da API Gemini
├── voice_capture.py     # Captura de voz
├── screenshot.py        # Captura de tela
├── gtts_speaker.py      # Síntese de voz
├── utils/
│   ├── cache_manager.py    # Gerenciamento de cache
│   ├── rate_limiter.py     # Controle de taxa
│   └── image_processor.py  # Processamento de imagens
├── requirements.txt     # Dependências
├── .env                # Configurações locais
└── .env.example        # Exemplo de configurações
```

## Segurança

- Chaves de API são armazenadas em variáveis de ambiente
- O arquivo `.env` está no `.gitignore`
- Arquivos temporários são limpos automaticamente
- Validação de entrada para prevenir injeção de comandos

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request
