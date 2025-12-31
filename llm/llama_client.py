# llm/llama_client.py

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import os
from typing import List, Dict
from config.llm_config import LLAMA_CONFIG
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LlamaClient:
    """
    Llama 3.2-1B Instruct client for natural language processing
    """
    
    def __init__(self):
        self.model_name = LLAMA_CONFIG['model_name']
        self.device = LLAMA_CONFIG['device']
        self.max_length = LLAMA_CONFIG['max_length']
        self.temperature = LLAMA_CONFIG['temperature']
        
        logger.info(f"🦙 Loading Llama model: {self.model_name}")
        logger.info(f"🔧 Device: {self.device}")
        
        # Get Hugging Face token from environment
        hf_token = os.getenv('HUGGINGFACE_TOKEN')
        if hf_token:
            logger.info("✅ Using Hugging Face authentication token")
        else:
            logger.warning("⚠️  No Hugging Face token found - some models may not be accessible")
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                token=hf_token
            )
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == 'cuda' else torch.float32,
                device_map='auto' if self.device == 'cuda' else None,
                trust_remote_code=True,
                token=hf_token
            )
            
            if self.device == 'cpu':
                self.model = self.model.to('cpu')
            
            # Create pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_length=self.max_length,
                temperature=self.temperature,
                top_p=LLAMA_CONFIG['top_p'],
                do_sample=LLAMA_CONFIG['do_sample'],
            )
            
            logger.info("✅ Llama model loaded successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error loading Llama model: {e}")
            raise
    
    def generate(self, prompt: str, max_new_tokens: int = 256) -> str:
        """
        Generate text from prompt
        """
        try:
            # Format as instruction
            formatted_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"
            
            # Generate
            outputs = self.pipeline(
                formatted_prompt,
                max_new_tokens=max_new_tokens,
                pad_token_id=self.tokenizer.eos_token_id,
                return_full_text=False
            )
            
            response = outputs[0]['generated_text'].strip()
            
            # Clean up response
            response = response.replace('<|eot_id|>', '').strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Error in generation: {e}")
            return f"Error: {str(e)}"
    
    def chat_completion(self, messages: List[Dict[str, str]], max_new_tokens: int = 256) -> str:
        """
        Chat completion compatible with OpenAI format
        """
        # Convert messages to single prompt
        prompt = ""
        for msg in messages:
            role = msg['role']
            content = msg['content']
            
            if role == 'system':
                prompt += f"System: {content}\n\n"
            elif role == 'user':
                prompt += f"User: {content}\n\n"
            elif role == 'assistant':
                prompt += f"Assistant: {content}\n\n"
        
        prompt += "Assistant:"
        
        return self.generate(prompt, max_new_tokens)
    
    def extract_keywords(self, query: str) -> List[str]:
        """
        Extract keywords from query
        """
        prompt = f"""Extract the main keywords from this query. Return only a comma-separated list of keywords, nothing else.

Query: {query}

Keywords:"""
        
        response = self.generate(prompt, max_new_tokens=50)
        
        # Parse keywords
        keywords = [k.strip().lower() for k in response.split(',')]
        return keywords
    
    def classify_query_intent(self, query: str, categories: List[str]) -> str:
        """
        Classify query into one of the given categories
        """
        categories_str = ', '.join(categories)
        
        prompt = f"""Classify this query into ONE of these categories: {categories_str}

Query: {query}

Category:"""
        
        response = self.generate(prompt, max_new_tokens=20)
        
        # Extract category
        response = response.strip().lower()
        
        # Find best match
        for category in categories:
            if category.lower() in response:
                return category
        
        return categories[0]  # Default to first category
    
    def extract_entity(self, query: str, entity_type: str) -> str:
        """
        Extract specific entity from query (e.g., product name, batch ID)
        """
        prompt = f"""Extract the {entity_type} from this query. Return ONLY the {entity_type}, nothing else.

Query: {query}

{entity_type}:"""
        
        response = self.generate(prompt, max_new_tokens=30)
        return response.strip()
    
    def summarize_results(self, query: str, results: List[Dict], max_items: int = 5) -> str:
        """
        Summarize query results in natural language
        """
        # Limit results for context window
        limited_results = results[:max_items]
        
        prompt = f"""Summarize these database results in a clear, natural way for the user.

User Query: {query}

Results:
{limited_results}

Summary:"""
        
        response = self.generate(prompt, max_new_tokens=200)
        return response.strip()
    
    def generate_cypher(self, user_query: str, schema: str) -> str:
        """
        Generate Cypher query from natural language
        """
        prompt = f"""You are a Neo4j Cypher expert. Generate a Cypher query based on the user's question and the graph schema.

Schema:
{schema}

User Question: {user_query}

Generate ONLY the Cypher query, nothing else. No explanations.

Cypher Query:"""
        
        response = self.generate(prompt, max_new_tokens=150)
        
        # Clean up response
        response = response.strip()
        
        # Remove markdown if present
        if '```' in response:
            response = response.split('```')[1]
            if response.startswith('cypher\n'):
                response = response[7:]
        
        return response.strip()

# Singleton instance
_llama_client = None

def get_llama_client() -> LlamaClient:
    """Get or create Llama client singleton"""
    global _llama_client
    if _llama_client is None:
        _llama_client = LlamaClient()
    return _llama_client