import json
import random
import os

# Set random seed for reproducibility
random.seed(42)

# Definitions of taxonomy and attributes
categories_map = {
    "T-Shirt": ("Clothing", "T-Shirts"),
    "Shirt": ("Clothing", "Shirts"),
    "Jeans": ("Clothing", "Jeans"),
    "Jacket": ("Clothing", "Jackets"),
    "Trousers": ("Clothing", "Trousers"),
    "Dress": ("Clothing", "Dresses"),
    "Saree": ("Clothing", "Sarees"),
    "Kurti": ("Clothing", "Kurtis"),
    "Running Shoes": ("Footwear", "Running Shoes"),
    "Sports Shoes": ("Footwear", "Sports Shoes"),
    "Casual Shoes": ("Footwear", "Casual Shoes"),
    "Sandals": ("Footwear", "Sandals"),
    "Slippers": ("Footwear", "Slippers"),
    "Mobile Phones": ("Electronics", "Mobile Phones"),
    "Earphones": ("Electronics", "Earphones"),
    "Headphones": ("Electronics", "Headphones"),
    "Chargers": ("Electronics", "Chargers"),
    "Smart Watches": ("Electronics", "Smart Watches"),
    "Wallets": ("Accessories", "Wallets"),
    "Belts": ("Accessories", "Belts"),
    "Handbags": ("Accessories", "Handbags"),
    "Backpacks": ("Accessories", "Backpacks"),
    "Cookware": ("Home & Kitchen", "Cookware"),
    "Bottles": ("Home & Kitchen", "Bottles"),
    "Storage Containers": ("Home & Kitchen", "Storage Containers"),
    "Kitchen Appliances": ("Home & Kitchen", "Kitchen Appliances"),
    "Home Decor": ("Home & Kitchen", "Home Decor")
}

product_types = list(categories_map.keys())

# Attribute vocabulary in English and Hindi
brands = ["Nike", "Adidas", "Puma", "Samsung", "Apple", "Philips", "Prestige", "Milton", "Tommy Hilfiger"]
brands_hi = {
    "Nike": "नाइके",
    "Adidas": "एडिडास",
    "Puma": "प्यूमा",
    "Samsung": "सैमसंग",
    "Apple": "एप्पल",
    "Philips": "फिलिप्स",
    "Prestige": "प्रेस्टीज",
    "Milton": "मिल्टन",
    "Tommy Hilfiger": "टॉमी हिलफिगर"
}

colors = {
    "Red": ["red", "Red", "लाल", "लाल रंग", "लाल रंग की", "लाल रंग का"],
    "Blue": ["blue", "Blue", "नीला", "नीले", "नीले रंग की", "नीले रंग का"],
    "Green": ["green", "Green", "हरा", "हरे", "हरे रंग की", "हरे रंग का"],
    "Black": ["black", "Black", "काला", "काले", "काले रंग की", "काले रंग का"],
    "White": ["white", "White", "सफेद", "सफ़ेद", "सफेद रंग की", "सफेद रंग का"],
    "Yellow": ["yellow", "Yellow", "पीला", "पीले", "पीले रंग की", "पीले रंग का"],
    "Grey": ["grey", "gray", "Grey", "ग्रे", "ग्रे रंग का", "स्लेटी"],
    "Pink": ["pink", "Pink", "गुलाबी", "गुलाबी रंग की", "गुलाबी रंग का"],
    "Brown": ["brown", "Brown", "भूरा", "भूरे", "भूरे रंग का", "भूरे रंग की"]
}

materials = {
    "Cotton": ["cotton", "Cotton", "कॉटन", "सूती", "सूती कपड़ा"],
    "Leather": ["leather", "Leather", "चमड़ा", "चमड़े", "चमड़े का", "चमड़े की"],
    "Denim": ["denim", "Denim", "डेनिम", "जींस कपड़ा"],
    "Polyester": ["polyester", "Polyester", "पॉलिएस्टर"],
    "Plastic": ["plastic", "Plastic", "प्लास्टिक"],
    "Metal": ["metal", "Metal", "मेटल", "धातु"],
    "Ceramic": ["ceramic", "Ceramic", "सिरेमिक"],
    "Glass": ["glass", "Glass", "ग्लास", "कांच"]
}

genders = {
    "Men": ["men", "mens", "Men", "Men's", "पुरुषों", "पुरुष", "पुरुषों के लिए"],
    "Women": ["women", "womens", "Women", "Women's", "महिला", "महिलाओं", "महिलाओं के लिए"],
    "Boys": ["boys", "Boys", "लड़कों", "लड़कों के लिए"],
    "Girls": ["girls", "Girls", "लड़कियों", "लड़कियों के लिए"],
    "Unisex": ["unisex", "Unisex", "यूनिसेक्स"]
}

sizes = {
    "S": ["S", "s", "small", "Small", "स्मॉल"],
    "M": ["M", "m", "medium", "Medium", "मीडियम"],
    "L": ["L", "l", "large", "Large", "लार्ज"],
    "XL": ["XL", "xl", "extra large", "Extra Large", "एक्स्ट्रा लार्ज"],
    "XXL": ["XXL", "xxl", "double xl"],
    "6": ["6", "size 6"],
    "7": ["7", "size 7"],
    "8": ["8", "size 8"],
    "9": ["9", "size 9"],
    "10": ["10", "size 10"],
    "11": ["11", "size 11"]
}

quantities = {
    "1": ["1", "1 pack", "1 piece", "१", "एक पीस"],
    "2": ["2", "2 pack", "pack of 2", "२", "दो पीस"],
    "3": ["3", "3 pack", "pack of 3", "३", "तीन पीस"],
    "4": ["4", "pack of 4", "४"],
    "5": ["5", "pack of 5", "५"]
}

# Product Type translation map for text variation
pt_variants = {
    "T-Shirt": ["tshirt", "t-shirt", "T-Shirt", "टीशर्ट", "टी-शर्ट", "टी शर्ट"],
    "Shirt": ["shirt", "Shirt", "शर्ट"],
    "Jeans": ["jeans", "Jeans", "जीन्स", "जींस"],
    "Jacket": ["jacket", "Jacket", "जैकेट"],
    "Trousers": ["trousers", "Trousers", "ट्राउजर", "ट्राउजर्स"],
    "Dress": ["dress", "Dress", "ड्रेस", "पोशाक"],
    "Saree": ["saree", "Saree", "साड़ी"],
    "Kurti": ["kurti", "Kurti", "कुर्ती"],
    "Running Shoes": ["running shoes", "Running Shoes", "रनिंग शूज़", "दौड़ने के जूते"],
    "Sports Shoes": ["sports shoes", "Sports Shoes", "स्पोर्ट्स शूज़", "खेलने के जूते"],
    "Casual Shoes": ["casual shoes", "Casual Shoes", "कैज़ुअल शूज़", "कैजुअल जूते"],
    "Sandals": ["sandals", "Sandals", "सैंडल"],
    "Slippers": ["slippers", "Slippers", "चप्पल"],
    "Mobile Phones": ["mobile phone", "phone", "Mobile Phone", "मोबाइल", "फोन"],
    "Earphones": ["earphones", "Earphones", "इयरफ़ोन", "इयरफोन"],
    "Headphones": ["headphones", "Headphones", "हेडफ़ोन", "हेडफोन"],
    "Chargers": ["charger", "Chargers", "चार्जर"],
    "Smart Watches": ["smart watch", "smartwatch", "Smart Watch", "स्मार्ट वॉच", "घड़ी"],
    "Wallets": ["wallet", "Wallet", "बटुआ", "पर्स"],
    "Belts": ["belt", "Belt", "बेल्ट"],
    "Handbags": ["handbag", "Handbags", "हैंडबैग"],
    "Backpacks": ["backpack", "Backpack", "बैकपैक", "बस्ता"],
    "Cookware": ["cookware", "Cookware", "बर्तन", "कढ़ाई"],
    "Bottles": ["bottle", "Bottle", "बोतल", "पानी की बोतल"],
    "Storage Containers": ["storage container", "containers", "कंटेनर", "डिब्बा"],
    "Kitchen Appliances": ["kitchen appliance", "appliances", "रसोई उपकरण", "मिक्सर"],
    "Home Decor": ["home decor", "decor", "सजावट", "घर की सजावट"]
}

def select_variant(word_list, lang):
    if lang == "en":
        sub = [w for w in word_list if w.isascii()]
    elif lang == "hi":
        sub = [w for w in word_list if not w.isascii()]
    else:
        sub = word_list
    
    if not sub:
        sub = word_list  # Fallback to entire list if language-specific filter yields empty
    return random.choice(sub)

def generate_samples():
    samples = []
    
    for _ in range(2200):
        # Pick random product type
        pt = random.choice(product_types)
        category, subcat = categories_map[pt]
        
        # Determine presence of attributes (with some probability of missing)
        has_color = random.random() < 0.8
        has_material = random.random() < 0.7
        has_gender = random.random() < 0.6 and category in ["Clothing", "Footwear"]
        has_size = random.random() < 0.6 and category in ["Clothing", "Footwear"]
        has_brand = random.random() < 0.5
        has_qty = random.random() < 0.3
        
        # Pick actual attribute values
        c_val = random.choice(list(colors.keys())) if has_color else None
        m_val = random.choice(list(materials.keys())) if has_material else None
        g_val = random.choice(list(genders.keys())) if has_gender else None
        s_val = random.choice(list(sizes.keys())) if has_size else None
        b_val = random.choice(brands) if has_brand else None
        q_val = random.choice(list(quantities.keys())) if has_qty else None
        
        # Choose language: en, hi, or mixed
        lang = random.choice(["en", "hi", "mixed"])
        
        # Select appropriate string variants depending on language
        pt_word = select_variant(pt_variants[pt], lang)
            
        c_word = select_variant(colors[c_val], lang) if c_val else None
        m_word = select_variant(materials[m_val], lang) if m_val else None
        g_word = select_variant(genders[g_val], lang) if g_val else None
        s_word = select_variant(sizes[s_val], lang) if s_val else None
        
        b_word = None
        if b_val:
            if lang == "en":
                b_word = b_val
            elif lang == "hi":
                b_word = brands_hi.get(b_val, b_val)
            else:
                b_word = random.choice([b_val, brands_hi.get(b_val, b_val)])
                
        q_word = select_variant(quantities[q_val], lang) if q_val else None
                
        # Build sentences using various templates
        text = ""
        if lang == "en":
            templates = [
                # Template 1: Color Material PT by Brand for Gender, Size
                lambda: f"{c_word or ''} {m_word or ''} {pt_word} {f'by {b_word}' if b_word else ''} {f'for {g_word}' if g_word else ''} {f'size {s_word}' if s_word else ''} {f'qty {q_word}' if q_word else ''}",
                # Template 2: Brand Gender Color PT in Material
                lambda: f"{b_word or ''} {g_word or ''} {c_word or ''} {pt_word} {f'in {m_word}' if m_word else ''} {f'size {s_word}' if s_word else ''}",
                # Template 3: Simple Description
                lambda: f"{c_word or ''} {pt_word} {f'size {s_word}' if s_word else ''} {f'- pack of {q_word}' if q_word else ''}"
            ]
            text = random.choice(templates)()
        elif lang == "hi":
            templates = [
                # Template 1: Gender ke liye Color Material PT, size Size
                lambda: f"{f'{g_word} के लिए' if g_word else ''} {c_word or ''} {m_word or ''} {pt_word} {f'साइज {s_word}' if s_word else ''} {f'मात्रा: {q_word}' if q_word else ''}",
                # Template 2: Color PT, Brand brand_name
                lambda: f"{c_word or ''} {pt_word} {f'ब्रांड {b_word}' if b_word else ''} {f'कपड़ा {m_word}' if m_word else ''}",
                # Template 3: Simple Hindi
                lambda: f"{c_word or ''} {m_word or ''} {pt_word} {f'मात्रा {q_word}' if q_word else ''}"
            ]
            text = random.choice(templates)()
        else: # Mixed / Hinglish
            templates = [
                # Template 1: Color color ka Material PT
                lambda: f"{c_word or ''} color का {m_word or ''} {pt_word} {f'for {g_word}' if g_word else ''} {f'size {s_word}' if s_word else ''}",
                # Template 2: Gender ke liye Brand ki Color PT
                lambda: f"{f'{g_word} के लिए' if g_word else ''} {b_word or ''} की {c_word or ''} {pt_word} {f'size {s_word}' if s_word else ''}",
                # Template 3: Qty pack of Color PT
                lambda: f"{f'{q_word} pack of' if q_word else ''} {c_word or ''} {pt_word} {f'made of {m_word}' if m_word else ''}"
            ]
            text = random.choice(templates)()
            
        # Clean extra spaces
        text = " ".join(text.split()).strip()
        # Randomize capitalization (for realism)
        if random.random() < 0.3 and lang == "en":
            text = text.lower()
        elif random.random() < 0.2 and lang == "en":
            text = text.upper()
            
        # Add to list
        if text:
            samples.append({
                "text": text,
                "language": "English" if lang == "en" else "Hindi" if lang == "hi" else "Mixed",
                "category": category,
                "subcategory": subcat,
                "attributes": {
                    "product_type": pt,
                    "brand": b_val,
                    "color": c_val,
                    "material": m_val,
                    "gender": g_val,
                    "size": s_val,
                    "quantity": q_val
                }
            })
            
    # Deduplicate based on text
    unique_samples = []
    seen_texts = set()
    for s in samples:
        t_lower = s["text"].lower()
        if t_lower not in seen_texts:
            seen_texts.add(t_lower)
            unique_samples.append(s)
            
    return unique_samples

def main():
    print("Generating raw dataset...")
    samples = generate_samples()
    print(f"Generated {len(samples)} unique samples.")
    
    # Ensure directories exist
    os.makedirs("ml/data/raw", exist_ok=True)
    
    with open("ml/data/raw/dataset.json", "w", encoding="utf-8") as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)
    print("Saved dataset to ml/data/raw/dataset.json")

if __name__ == "__main__":
    main()
