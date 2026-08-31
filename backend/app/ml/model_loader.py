import os
import numpy as np
import tensorflow as tf
from .tokenizer import CustomTokenizer

class CatalogSLMModel:
    def __init__(self, model_path, tokenizer_path):
        self.tokenizer = CustomTokenizer(tokenizer_path)
        
        if not os.path.exists(model_path):
            # Check for alternative paths (e.g. .h5 vs .keras)
            alt_path = model_path.replace(".keras", ".h5") if model_path.endswith(".keras") else model_path.replace(".h5", ".keras")
            if os.path.exists(alt_path):
                model_path = alt_path
            else:
                raise FileNotFoundError(f"Model file not found at {model_path} or {alt_path}")
                
        print(f"Loading TensorFlow model from: {model_path} ...")
        self.model = tf.keras.models.load_model(model_path)
        print("Model loaded successfully.")
        
    def predict(self, text):
        input_ids = self.tokenizer.encode(text)
        input_batch = np.array([input_ids], dtype=np.int32)
        
        # Run inference
        preds = self.model.predict(input_batch, verbose=0)
        
        results = {}
        confidences = {}
        
        # Map predictions back to labels
        for head_name, pred_probs in preds.items():
            prob_dist = pred_probs[0]  # Extract single item
            pred_idx = np.argmax(prob_dist)
            conf = float(prob_dist[pred_idx])
            
            label_list = self.tokenizer.labels[head_name]
            label = label_list[pred_idx]
            
            results[head_name] = label
            confidences[head_name] = conf
            
        # Overall confidence is average of attribute prediction confidences
        overall_conf = float(np.mean(list(confidences.values())))
        confidences["overall"] = overall_conf
        
        return results, confidences

# Global reference
model_instance = None

def get_model():
    return model_instance

def load_global_model(model_path, tokenizer_path):
    global model_instance
    if model_instance is None:
        model_instance = CatalogSLMModel(model_path, tokenizer_path)
    return model_instance
