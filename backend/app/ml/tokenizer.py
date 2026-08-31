import json
import re
import os

class CustomTokenizer:
    def __init__(self, tokenizer_path):
        if not os.path.exists(tokenizer_path):
            raise FileNotFoundError(f"Tokenizer config not found at {tokenizer_path}")
            
        with open(tokenizer_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.vocab = data["vocab"]
        self.labels = data["labels"]
        self.max_len = data["max_len"]
        
    def tokenize(self, text):
        # Lowercase
        text = text.lower()
        # Clean special chars / punctuation
        text = re.sub(r'[,.\-/\|:;?!\(\)]', ' ', text)
        tokens = text.split()
        return tokens
        
    def encode(self, text):
        tokens = self.tokenize(text)
        # Map to indices, fall back to 1 (<UNK>)
        indices = [self.vocab.get(t, 1) for t in tokens]
        
        # Pad with 0 (<PAD>) or truncate
        if len(indices) < self.max_len:
            indices = indices + [0] * (self.max_len - len(indices))
        else:
            indices = indices[:self.max_len]
            
        return indices
