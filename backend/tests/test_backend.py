import pytest
import os
import json
from fastapi.testclient import TestClient

# We will write unit tests for the core logic
from backend.app.ml.tokenizer import CustomTokenizer
from backend.app.services.normalization import Normalizer
from backend.app.services.taxonomy_mapper import TaxonomyMapper

# Setup paths
NORM_PATH = "backend/app/data/normalization.json"
TAX_PATH = "backend/app/data/taxonomy.json"
TOKENIZER_PATH = "ml/models/catalog_slm/tokenizer.json"

@pytest.fixture
def normalizer():
    return Normalizer(NORM_PATH)

@pytest.fixture
def taxonomy_mapper():
    return TaxonomyMapper(TAX_PATH)

def test_normalization_direct_mapping(normalizer):
    # Test English and Hindi color normalization
    assert normalizer.normalize("colors", "लाल") == "Red"
    assert normalizer.normalize("colors", "नीले") == "Blue"
    assert normalizer.normalize("colors", "black") == "Black"
    
    # Test material normalization
    assert normalizer.normalize("materials", "सूती") == "Cotton"
    assert normalizer.normalize("materials", "कॉटन") == "Cotton"
    assert normalizer.normalize("materials", "leather") == "Leather"
    
    # Test size normalization
    assert normalizer.normalize("sizes", "large") == "L"
    assert normalizer.normalize("sizes", "स्मॉल") == "S"

def test_normalization_fallback_extraction(normalizer):
    # Test rule-based extraction from text
    desc = "लाल रंग की कॉटन टीशर्ट पुरुषों के लिए"
    assert normalizer.extract_with_rules(desc, "colors") == "Red"
    assert normalizer.extract_with_rules(desc, "materials") == "Cotton"
    assert normalizer.extract_with_rules(desc, "genders") == "Men"
    assert normalizer.extract_with_rules(desc, "product_types") == "T-Shirt"

def test_taxonomy_mapping(taxonomy_mapper):
    # Test clothing mapping
    path_info1 = taxonomy_mapper.map_to_path("Clothing", "T-Shirt", "Men")
    assert path_info1["category"] == "Clothing"
    assert path_info1["subcategory"] == "T-Shirts"
    assert path_info1["taxonomy_path"] == ["Clothing", "Men's Clothing", "T-Shirts"]
    
    # Test footwear mapping
    path_info2 = taxonomy_mapper.map_to_path("Footwear", "Running Shoes", None)
    assert path_info2["category"] == "Footwear"
    assert path_info2["subcategory"] == "Running Shoes"
    assert path_info2["taxonomy_path"] == ["Footwear", "Footwear", "Running Shoes"]

def test_tokenizer_encoding():
    # If tokenizer is trained, verify it
    if os.path.exists(TOKENIZER_PATH):
        tok = CustomTokenizer(TOKENIZER_PATH)
        tokens = tok.tokenize("Red cotton shirt for men")
        assert "red" in tokens
        assert "cotton" in tokens
        
        encoded = tok.encode("Red cotton shirt")
        assert len(encoded) == tok.max_len
        assert encoded[0] > 0
