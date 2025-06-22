"""
Módulo responsável pelo gerenciamento do histórico de conversas.
"""
import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class ConversationHistory:
    def __init__(self, db_path: str = "conversation_history.db"):
        """
        Inicializa o gerenciador de histórico de conversas.
        
        Args:
            db_path: Caminho para o banco de dados SQLite
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Inicializa o banco de dados com as tabelas necessárias."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Cria tabela de conversas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    question TEXT NOT NULL,
                    response TEXT NOT NULL,
                    images TEXT,  -- JSON array com paths das imagens
                    tags TEXT     -- JSON array com tags para busca
                )
            """)
            
            # Cria índices para melhor performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_timestamp 
                ON conversations(timestamp)
            """)
            conn.commit()

    def add_conversation(
        self, 
        question: str, 
        response: str, 
        images: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> int:
        """
        Adiciona uma nova conversa ao histórico.
        
        Args:
            question: Pergunta do usuário
            response: Resposta do sistema
            images: Lista de caminhos das imagens usadas
            tags: Lista de tags para categorização
            
        Returns:
            ID da conversa no banco de dados
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO conversations (question, response, images, tags)
                VALUES (?, ?, ?, ?)
                """,
                (
                    question,
                    response,
                    json.dumps(images) if images else None,
                    json.dumps(tags) if tags else None
                )
            )
            conn.commit()
            return cursor.lastrowid

    def get_conversation(self, conversation_id: int) -> Optional[Dict]:
        """
        Recupera uma conversa específica do histórico.
        
        Args:
            conversation_id: ID da conversa
            
        Returns:
            Dicionário com os dados da conversa ou None se não encontrada
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM conversations WHERE id = ?",
                (conversation_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'question': row['question'],
                    'response': row['response'],
                    'images': json.loads(row['images']) if row['images'] else None,
                    'tags': json.loads(row['tags']) if row['tags'] else None
                }
            return None

    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """
        Recupera as conversas mais recentes.
        
        Args:
            limit: Número máximo de conversas para retornar
            
        Returns:
            Lista de conversas ordenadas por data (mais recente primeiro)
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM conversations 
                ORDER BY timestamp DESC 
                LIMIT ?
                """,
                (limit,)
            )
            
            return [{
                'id': row['id'],
                'timestamp': row['timestamp'],
                'question': row['question'],
                'response': row['response'],
                'images': json.loads(row['images']) if row['images'] else None,
                'tags': json.loads(row['tags']) if row['tags'] else None
            } for row in cursor.fetchall()]

    def search_conversations(self, query: str) -> List[Dict]:
        """
        Pesquisa conversas por texto ou tags.
        
        Args:
            query: Texto para pesquisar
            
        Returns:
            Lista de conversas que correspondem à pesquisa
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM conversations 
                WHERE question LIKE ? 
                OR response LIKE ? 
                OR tags LIKE ?
                ORDER BY timestamp DESC
                """,
                (f"%{query}%", f"%{query}%", f"%{query}%")
            )
            
            return [{
                'id': row['id'],
                'timestamp': row['timestamp'],
                'question': row['question'],
                'response': row['response'],
                'images': json.loads(row['images']) if row['images'] else None,
                'tags': json.loads(row['tags']) if row['tags'] else None
            } for row in cursor.fetchall()]

    def get_conversation_count(self) -> int:
        """
        Retorna o número total de conversas no histórico.
        
        Returns:
            Número total de conversas
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversations")
            return cursor.fetchone()[0]

    def format_conversation(self, conversation: Dict) -> str:
        """
        Formata uma conversa para exibição.
        
        Args:
            conversation: Dicionário com dados da conversa
            
        Returns:
            Texto formatado da conversa
        """
        dt = datetime.fromisoformat(conversation['timestamp'].replace('Z', '+00:00'))
        formatted_date = dt.strftime("%d/%m/%Y %H:%M:%S")
        
        return (
            f"Data: {formatted_date}\n"
            f"Pergunta: {conversation['question']}\n"
            f"Resposta: {conversation['response']}\n"
            f"{'Tags: ' + ', '.join(conversation['tags']) if conversation.get('tags') else ''}\n"
        )
