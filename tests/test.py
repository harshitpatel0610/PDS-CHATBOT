from chatbot.entities.extractor import EntityExtractor

entities = EntityExtractor.extract(

    "I want to apply for BPL ration card in Karnataka",

    "ration_card_apply"

)

print(entities)