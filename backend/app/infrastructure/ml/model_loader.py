"""ML model loader"""
import logging
import torch
from typing import Optional, Union
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForSequenceClassification, AutoTokenizer

logger = logging.getLogger(__name__)


class ModelLoader:
    """Loads and manages ML models"""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model: Optional[Union[SentenceTransformer, AutoModelForSequenceClassification]] = None
        self.tokenizer: Optional[AutoTokenizer] = None
        self.device: Optional[torch.device] = None
        self.is_sentence_transformer: bool = False
    
    def load_model(self):
        """Load model and determine device"""
        # Determine device
        if torch.cuda.is_available():
            self.device = torch.device('cuda')
        elif torch.backends.mps.is_available():
            self.device = torch.device('mps')
        else:
            self.device = torch.device('cpu')
        
        logger.info(f"Using device: {self.device}")
        logger.info(f"Loading model from: {self.model_path}")
        
        # Try loading as Sentence Transformer first
        try:
            self.model = SentenceTransformer(self.model_path, device=str(self.device))
            self.is_sentence_transformer = True
            logger.info("✓ Loaded as Sentence Transformer model")
        except Exception:
            # Fall back to classification model
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_path,
                    num_labels=1,
                    problem_type='regression'
                )
                self.model.to(self.device)
                self.model.eval()
                self.is_sentence_transformer = False
                logger.info("✓ Loaded as classification model")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise RuntimeError(f"Model loading failed: {e}")
        
        logger.info("✓ Model loaded successfully")
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None
    
    def get_model(self):
        """Get the loaded model"""
        return self.model
    
    def get_tokenizer(self):
        """Get the tokenizer (for classification models)"""
        return self.tokenizer
    
    def get_device(self):
        """Get the device"""
        return self.device
