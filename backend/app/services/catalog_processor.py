import time
import uuid
import os
from ..ml.model_loader import get_model
from .normalization import Normalizer
from .taxonomy_mapper import TaxonomyMapper

class CatalogProcessor:
    def __init__(self, normalization_path, taxonomy_path):
        self.normalizer = Normalizer(normalization_path)
        self.taxonomy_mapper = TaxonomyMapper(taxonomy_path)
        
    def process_text(self, text, language_override="auto"):
        t0 = time.time()
        
        # Get model instance
        model = get_model()
        if model is None:
            raise RuntimeError("ML model has not been loaded. Please wait for training to complete.")
            
        # Run inference
        preds, confs = model.predict(text)
        
        # Detected language
        detected_lang = preds.get("language", "Mixed")
        if language_override != "auto":
            detected_lang = language_override
            
        # Standardize attributes using Normalizer (ML predicts, Normalizer standardizes)
        extracted_attributes = {}
        confidence_scores = {}
        
        # Controlled fields to extract
        fields = ["product_type", "color", "material", "gender", "size", "brand", "quantity"]
        
        for field in fields:
            ml_pred = preds.get(field, "None")
            ml_conf = confs.get(field, 0.0)
            
            # Map predictions to canonical names
            canon_val = None
            if ml_pred != "None":
                if field == "color":
                    canon_val = self.normalizer.normalize("colors", ml_pred)
                elif field == "material":
                    canon_val = self.normalizer.normalize("materials", ml_pred)
                elif field == "gender":
                    canon_val = self.normalizer.normalize("genders", ml_pred)
                elif field == "size":
                    canon_val = self.normalizer.normalize("sizes", ml_pred)
                elif field == "product_type":
                    canon_val = self.normalizer.normalize("product_types", ml_pred)
                elif field == "brand":
                    canon_val = self.normalizer.normalize("brands", ml_pred)
                elif field == "quantity":
                    # Keep raw/normalized quantity
                    canon_val = ml_pred
                    
            # Fallback to rules if ML predicted None or confidence is very low (< 0.50)
            if not canon_val or ml_conf < 0.50:
                rule_val = None
                if field == "color":
                    rule_val = self.normalizer.extract_with_rules(text, "colors")
                elif field == "material":
                    rule_val = self.normalizer.extract_with_rules(text, "materials")
                elif field == "gender":
                    rule_val = self.normalizer.extract_with_rules(text, "genders")
                elif field == "size":
                    rule_val = self.normalizer.extract_with_rules(text, "sizes")
                elif field == "product_type":
                    rule_val = self.normalizer.extract_with_rules(text, "product_types")
                elif field == "brand":
                    # Since brands are open-ended, do string scan
                    for brand in ["Nike", "Adidas", "Puma", "Samsung", "Apple", "Philips", "Prestige", "Milton", "Tommy Hilfiger"]:
                        if brand.lower() in text.lower():
                            rule_val = brand
                            break
                            
                if rule_val:
                    canon_val = rule_val
                    # Assign a fixed fallback rule confidence
                    ml_conf = max(ml_conf, 0.85)
                    
            extracted_attributes[field] = canon_val
            confidence_scores[field] = round(ml_conf, 3)
            
        # Run Taxonomy mapping
        taxonomy_info = self.taxonomy_mapper.map_to_path(
            extracted_attributes.get("category"),  # from subcat lookup
            extracted_attributes.get("product_type"),
            extracted_attributes.get("gender")
        )
        
        # Build canonical product name
        name_parts = []
        brand = extracted_attributes.get("brand")
        gender = extracted_attributes.get("gender")
        color = extracted_attributes.get("color")
        material = extracted_attributes.get("material")
        pt = extracted_attributes.get("product_type") or "Product"
        
        if brand:
            name_parts.append(brand)
        if gender:
            name_parts.append(gender + "'s" if gender in ["Men", "Women"] else gender)
        if color:
            name_parts.append(color)
        if material:
            name_parts.append(material)
            
        name_parts.append(pt)
        product_name = " ".join(name_parts)
        
        # Calculate overall confidence
        confidence_scores["overall"] = round(float(np.mean(list(confidence_scores.values()))), 3)
        
        processing_time = int((time.time() - t0) * 1000)
        
        # Status determination based on confidence
        status = "Draft"
        if confidence_scores["overall"] < 0.70:
            status = "Needs Review"
            
        catalog_id = str(uuid.uuid4())
        
        return {
            "catalog_id": catalog_id,
            "original_text": text,
            "detected_language": detected_lang,
            "product_name": product_name,
            "category": taxonomy_info["category"],
            "subcategory": taxonomy_info["subcategory"],
            "taxonomy_path": taxonomy_info["taxonomy_path"],
            "attributes": extracted_attributes,
            "confidence": confidence_scores,
            "processing_time_ms": processing_time,
            "status": status
        }

# Dummy numpy mean fallback if numpy is not loaded yet
import numpy as np
