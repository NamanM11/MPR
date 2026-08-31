import json
import re
import os

class Normalizer:
    def __init__(self, normalization_path):
        if not os.path.exists(normalization_path):
            raise FileNotFoundError(f"Normalization file not found at {normalization_path}")
            
        with open(normalization_path, "r", encoding="utf-8") as f:
            self.rules = json.load(f)
            
    def normalize(self, field, value):
        if not value or value == "None" or value == "null":
            return None
            
        val_str = str(value).strip().lower()
        
        # Check mapping dictionary
        rule_map = self.rules.get(field, {})
        if val_str in rule_map:
            return rule_map[val_str]
            
        # Try reverse lookup / contains
        for key, canonical in rule_map.items():
            if val_str == key.lower():
                return canonical
                
        # Capitalize standard fallback
        return str(value).title()
        
    def extract_with_rules(self, text, field):
        """Rule-based extractor for attributes in text as a fallback."""
        text_lower = text.lower()
        rule_map = self.rules.get(field, {})
        
        # Sort keys by length descending to match longest matches first (e.g., "लाल रंग" before "लाल")
        sorted_keys = sorted(rule_map.keys(), key=len, reverse=True)
        
        for key in sorted_keys:
            # For Hindi words, use simple inclusion. For English, check word boundary.
            has_hindi = any(0x0900 <= ord(c) <= 0x097F for c in key)
            if has_hindi:
                if key in text_lower:
                    return rule_map[key]
            else:
                pattern = r'\b' + re.escape(key) + r'\b'
                if re.search(pattern, text_lower):
                    return rule_map[key]
                    
        return None
