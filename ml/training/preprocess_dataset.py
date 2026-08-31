import json
import os
import random
import re

random.seed(42)

# Normalization target label sets
LABELS = {
    "category": [
        "Clothing", "Footwear", "Electronics", "Accessories", "Home & Kitchen"
    ],
    "subcategory": [
        "T-Shirts", "Shirts", "Jeans", "Jackets", "Trousers", 
        "Dresses", "Sarees", "Kurtis", "Running Shoes", "Sports Shoes", 
        "Casual Shoes", "Sandals", "Slippers", "Mobile Phones", "Earphones", 
        "Headphones", "Chargers", "Smart Watches", "Wallets", "Belts", 
        "Handbags", "Backpacks", "Cookware", "Bottles", "Storage Containers", 
        "Kitchen Appliances", "Home Decor"
    ],
    "product_type": [
        "T-Shirt", "Shirt", "Jeans", "Jacket", "Trousers", 
        "Dress", "Saree", "Kurti", "Running Shoes", "Sports Shoes", 
        "Casual Shoes", "Sandals", "Slippers", "Mobile Phones", "Earphones", 
        "Headphones", "Chargers", "Smart Watches", "Wallets", "Belts", 
        "Handbags", "Backpacks", "Cookware", "Bottles", "Storage Containers", 
        "Kitchen Appliances", "Home Decor"
    ],
    "color": ["Red", "Blue", "Green", "Black", "White", "Yellow", "Grey", "Pink", "Brown", "None"],
    "material": ["Cotton", "Leather", "Denim", "Polyester", "Plastic", "Metal", "Ceramic", "Glass", "None"],
    "gender": ["Men", "Women", "Boys", "Girls", "Unisex", "None"],
    "size": ["S", "M", "L", "XL", "XXL", "6", "7", "8", "9", "10", "11", "None"],
    "brand": ["Nike", "Adidas", "Puma", "Samsung", "Apple", "Philips", "Prestige", "Milton", "Tommy Hilfiger", "None"],
    "quantity": ["1", "2", "3", "4", "5", "None"],
    "language": ["English", "Hindi", "Mixed"]
}

MAX_LEN = 20

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[,.\-/\|:;?!\(\)]', ' ', text)
    tokens = text.split()
    return tokens

def main():
    print("Preprocessing dataset...")
    
    raw_path = "ml/data/raw/dataset.json"
    if not os.path.exists(raw_path):
        print(f"Error: {raw_path} not found. Run generate_dataset.py first.")
        return
        
    with open(raw_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Build vocabulary
    vocab_counter = {}
    for sample in data:
        tokens = preprocess_text(sample["text"])
        for t in tokens:
            vocab_counter[t] = vocab_counter.get(t, 0) + 1
            
    # Sort vocab by frequency
    sorted_vocab = sorted(vocab_counter.items(), key=lambda x: x[1], reverse=True)
    
    # Map tokens to indices (0: PAD, 1: UNK)
    vocab = {"<PAD>": 0, "<UNK>": 1}
    for idx, (token, _) in enumerate(sorted_vocab):
        vocab[token] = idx + 2
        
    print(f"Vocabulary size: {len(vocab)}")
    
    # Save tokenizer and label mappings
    os.makedirs("ml/models/catalog_slm", exist_ok=True)
    
    tokenizer_data = {
        "vocab": vocab,
        "labels": LABELS,
        "max_len": MAX_LEN
    }
    
    with open("ml/models/catalog_slm/tokenizer.json", "w", encoding="utf-8") as f:
        json.dump(tokenizer_data, f, ensure_ascii=False, indent=2)
    print("Saved tokenizer and label mappings to ml/models/catalog_slm/tokenizer.json")
    
    # Process samples
    processed_samples = []
    for sample in data:
        tokens = preprocess_text(sample["text"])
        # Map to indices
        token_indices = [vocab.get(t, 1) for t in tokens]
        # Pad or truncate
        if len(token_indices) < MAX_LEN:
            token_indices = token_indices + [0] * (MAX_LEN - len(token_indices))
        else:
            token_indices = token_indices[:MAX_LEN]
            
        # Map labels to indices
        label_indices = {}
        
        # Category
        label_indices["category"] = LABELS["category"].index(sample["category"])
        label_indices["subcategory"] = LABELS["subcategory"].index(sample["subcategory"])
        label_indices["language"] = LABELS["language"].index(sample["language"])
        
        # Attributes
        for attr in ["product_type", "color", "material", "gender", "size", "brand", "quantity"]:
            val = sample["attributes"][attr]
            if val is None:
                val = "None"
            label_indices[attr] = LABELS[attr].index(val)
            
        processed_samples.append({
            "text": sample["text"],
            "input_ids": token_indices,
            "targets": label_indices
        })
        
    # Shuffle and split (80/10/10)
    random.shuffle(processed_samples)
    
    total = len(processed_samples)
    train_end = int(0.8 * total)
    val_end = int(0.9 * total)
    
    train_data = processed_samples[:train_end]
    val_data = processed_samples[train_end:val_end]
    test_data = processed_samples[val_end:]
    
    print(f"Dataset split: Train={len(train_data)}, Val={len(val_data)}, Test={len(test_data)}")
    
    # Save processed files
    os.makedirs("ml/data/processed", exist_ok=True)
    
    with open("ml/data/processed/train.json", "w", encoding="utf-8") as f:
        json.dump(train_data, f, ensure_ascii=False, indent=2)
    with open("ml/data/processed/val.json", "w", encoding="utf-8") as f:
        json.dump(val_data, f, ensure_ascii=False, indent=2)
    with open("ml/data/processed/test.json", "w", encoding="utf-8") as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
        
    print("Preprocessed dataset successfully saved.")

if __name__ == "__main__":
    main()
