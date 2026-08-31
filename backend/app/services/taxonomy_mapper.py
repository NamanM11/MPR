import json
import os

class TaxonomyMapper:
    def __init__(self, taxonomy_path):
        if not os.path.exists(taxonomy_path):
            raise FileNotFoundError(f"Taxonomy file not found at {taxonomy_path}")
            
        with open(taxonomy_path, "r", encoding="utf-8") as f:
            self.taxonomy = json.load(f)
            
    def map_to_path(self, predicted_category, predicted_subcategory, gender=None):
        # Resolve category if predicted_category is not matching keys
        category = predicted_category
        if category not in self.taxonomy:
            # Fallback scan: find which category contains this subcategory
            found = False
            for cat, subcat_groups in self.taxonomy.items():
                for group, subcats in subcat_groups.items():
                    if predicted_subcategory in subcats:
                        category = cat
                        found = True
                        break
                if found:
                    break
                    
        # Default fallback
        if category not in self.taxonomy:
            category = list(self.taxonomy.keys())[0]
            
        subcat_groups = self.taxonomy[category]
        
        # Search for the subcategory within the category's groups
        target_group = None
        target_subcat = None
        
        # Disambiguate if multiple groups contain the same subcategory name (e.g. T-Shirts in Men and Women)
        matching_groups = []
        for group, subcats in subcat_groups.items():
            if predicted_subcategory in subcats:
                matching_groups.append(group)
                target_subcat = predicted_subcategory
                
        if len(matching_groups) == 1:
            target_group = matching_groups[0]
        elif len(matching_groups) > 1:
            # Disambiguate by gender
            gender_lower = str(gender).lower() if gender else ""
            if "women" in gender_lower or "girl" in gender_lower:
                # Find women group
                women_groups = [g for g in matching_groups if "women" in g.lower() or "girl" in g.lower()]
                target_group = women_groups[0] if women_groups else matching_groups[0]
            else:
                # Find men group
                men_groups = [g for g in matching_groups if "men" in g.lower() or "boy" in g.lower()]
                target_group = men_groups[0] if men_groups else matching_groups[0]
        else:
            # Fallback subcategory match - if not found, choose the first subcategory in first group
            target_group = list(subcat_groups.keys())[0]
            target_subcat = subcat_groups[target_group][0]
            
        return {
            "category": category,
            "subcategory": target_subcat,
            "taxonomy_path": [category, target_group, target_subcat]
        }
