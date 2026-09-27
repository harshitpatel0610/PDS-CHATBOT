from .matcher import EntityMatcher
from .models import Entity

ENTITY_CONFIG = {
    "ration_card_apply": ["card_types", "states", "districts"],
    "ration_card_eligibility": ["card_types", "states", "districts"],
    "documents_required": ["card_types", "states", "districts"],
    "ration_card_online_offline": ["card_types", "states", "districts"],
    "ration_card_types": ["states", "districts"],
    "ration_card_update": ["states", "districts"],
    "ration_card_status": ["states", "districts"],
    
    "add_family_member": ["relations", "states"],
    "remove_family_member": ["relations", "states"],
    "transaction_history": ["states"],
    "ration_price": ["commodities", "states", "card_types"],
    "ration_items_list": ["commodities", "states", "card_types"]
}

THRESHOLDS = {
    "card_types": 90,
    "states": 88,
    "districts": 100,      
    "commodities": 88,
    "relations": 90
}

AMBIGUITY_MARGIN = {
    "states": 8,
    "commodities": 8,
    "card_types": 10,
    "relations": 10,
}

class EntityExtractor:

    @staticmethod
    def extract(query, intent):

        entities = []
        # Fallback: if intent not in config, always try to extract state and card_type anyway to be safe!
        entity_sets = ENTITY_CONFIG.get(intent, ["states", "card_types", "districts"])

        for entity_type in entity_sets:
            matches = EntityMatcher.find(query, entity_type)
            if not matches:
                continue
            threshold = THRESHOLDS.get(entity_type, 90)
            margin = AMBIGUITY_MARGIN.get(entity_type, 8)
            
            exact_matches = [(value, score) for value, score in matches if score == 100]
            if exact_matches:
                for value, score in exact_matches:
                    entities.append(Entity(entity_type=entity_type, value=value, confidence=1.0))
                continue
                
            value, score = matches[0]
            if score < threshold:
                continue
                
            if len(matches) > 1:
                next_value, next_score = matches[1]
                if score - next_score < margin:
                    continue
            entities.append(Entity(entity_type=entity_type, value=value, confidence=score / 100))

        has_state = any(e.entity_type == "states" for e in entities)
        if not has_state:
            district_entity = next((e for e in entities if e.entity_type == "districts"), None)
            if district_entity:
                from .registry import ENTITY_DATA
                for district_data in ENTITY_DATA.get("districts", []):
                    if isinstance(district_data, dict) and district_data.get("name") == district_entity.value:
                        inferred_state = district_data.get("state")
                        if inferred_state:
                            entities.append(Entity(entity_type="states", value=inferred_state, confidence=1.0))
                        break
        return entities
