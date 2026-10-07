import re
from difflib import SequenceMatcher

from ..database import get_products


NUMBER_WORDS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
    "twenty": "20",
}
GENERIC_PRODUCT_WORDS = {
    "mobile", "mobiles", "phone", "phones", "smartphone", "smartphones",
    "product", "products",
}
STORAGE_PATTERN = re.compile(r"(?<!\w)(\d+(?:\.\d+)?\s*(?:tb|gb|mb))(?!\w)", re.IGNORECASE)


def _normalize_value(value):
    return re.sub(r"[^a-z0-9]+", "", str(value).casefold())


class ProductResolver:
    def __init__(self, normalizer):
        self.normalizer = normalizer

    def _canonical_identity(self, text, product=None):
        normalized = str(text).casefold()
        normalized = re.sub(r"(?<=[a-z])(?=\d)|(?<=\d)(?=[a-z])", " ", normalized)
        normalized = STORAGE_PATTERN.sub(" ", normalized)
        for word, digit in NUMBER_WORDS.items():
            normalized = re.sub(rf"\b{word}\b", digit, normalized)

        for alias, canonical in self.normalizer.rules.get("colors", {}).items():
            if any("\u0900" <= char <= "\u097f" for char in alias):
                normalized = normalized.replace(alias.casefold(), " ")
            else:
                normalized = re.sub(rf"\b{re.escape(alias.casefold())}\b", " ", normalized)

        if product:
            for value in (product.get("brand"), product.get("category"), product.get("subcategory")):
                if value:
                    normalized = re.sub(rf"\b{re.escape(value.casefold())}\b", " ", normalized)

        tokens = re.findall(r"[a-z0-9]+", normalized)
        tokens = [token for token in tokens if token not in GENERIC_PRODUCT_WORDS]
        return " ".join(tokens)

    def _find_product(self, text, products):
        candidates = []
        for product in products:
            aliases = [product["product_name"]]
            model = product.get("attributes", {}).get("model")
            if model and model.casefold() != product["product_name"].casefold():
                aliases.append(model)

            request_key = self._canonical_identity(text, product)
            alias_keys = [self._canonical_identity(alias, product) for alias in aliases]
            alias_keys = [alias for alias in alias_keys if alias]
            if request_key and request_key in alias_keys:
                return product, 1.0, "normalized_exact"

            for alias_key in alias_keys:
                score = SequenceMatcher(None, request_key, alias_key).ratio()
                if score >= 0.80:
                    candidates.append((score, product))

        if candidates:
            score, product = max(candidates, key=lambda candidate: candidate[0])
            return product, round(score, 3), "fuzzy"
        return None, 0.0, "new_product"

    def _extract_requested_variant(self, text, product):
        requested = {}
        storage_match = STORAGE_PATTERN.search(text)
        if storage_match:
            requested["storage"] = re.sub(r"\s+", "", storage_match.group(1)).upper()

        color = self.normalizer.extract_with_rules(text, "colors")
        if color:
            requested["color"] = color

        variant_keys = {
            str(key).casefold()
            for variant in product["valid_variants"]
            for key in variant
        }
        for key in variant_keys - requested.keys():
            values = {
                str(variant[key])
                for variant in product["valid_variants"]
                if key in variant
            }
            for value in values:
                if re.search(rf"(?<!\w){re.escape(value)}(?!\w)", text, re.IGNORECASE):
                    requested[key] = value
                    break
        return requested

    def _match_variant(self, requested, variants):
        if not requested:
            return None, None, []

        reasons = []
        for key, value in requested.items():
            known_values = {
                _normalize_value(variant[key])
                for variant in variants
                if key in variant
            }
            if _normalize_value(value) not in known_values:
                reasons.append(f"{value} is not a known {key} variant")

        if reasons:
            return False, None, reasons

        for variant in variants:
            if all(
                key in variant and _normalize_value(variant[key]) == _normalize_value(value)
                for key, value in requested.items()
            ):
                return True, variant, []

        return False, None, ["The requested variant combination is not available"]

    def resolve(self, text):
        products = get_products()
        product, confidence, method = self._find_product(text, products)
        if product is None:
            return {
                "existing_product": False,
                "matched_product_id": None,
                "product_match": False,
                "variant_match": None,
                "product_resolution_confidence": confidence,
                "resolution_method": method,
                "matched_variant": None,
                "requested_variant": {},
                "resolution_reasons": [],
                "product_metadata": None,
            }

        requested_variant = self._extract_requested_variant(text, product)
        variant_match, matched_variant, reasons = self._match_variant(
            requested_variant,
            product["valid_variants"],
        )
        return {
            "existing_product": True,
            "matched_product_id": product["product_id"],
            "product_match": True,
            "variant_match": variant_match,
            "product_resolution_confidence": confidence,
            "resolution_method": method,
            "matched_variant": matched_variant,
            "requested_variant": requested_variant,
            "resolution_reasons": reasons,
            "product_metadata": product,
        }
