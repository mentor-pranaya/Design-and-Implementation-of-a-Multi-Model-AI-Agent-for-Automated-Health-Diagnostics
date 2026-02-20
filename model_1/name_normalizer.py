from typing import Dict
from .dataset_loader import load_medical_ner
from .synonym_mapper import normalize_name as synonym_normalize


class NameNormalizer:
    def __init__(self, ner_base_path: str = "datasets/medical_ner"):
        # dataset-driven mapping alias->canonical
        self.mapping: Dict[str, str] = load_medical_ner(ner_base_path)

    def normalize(self, name: str) -> str:
        if not name:
            return name
        # first apply lightweight synonym normalization
        syn = synonym_normalize(name)
        if syn != name:
            return syn
        key = name.strip().lower()
        return self.mapping.get(key, name)
