import re

class CoreferenceResolver:
    """Simple rule-based coreference resolver for pronouns using context."""
    def __init__(self):
        self.pronouns_to_resolve = {'he', 'him', 'his', 'she', 'her', 'hers', 'it', 'its'}

    def resolve(self, text: str, context_entities: list):
        """
        Replace pronouns in `text` with the most recent matching entity from `context_entities`.
        (Simplistic matching: replace 'he/she' with last PERSON, 'it' with last ORG/PRODUCT)
        """
        if not text:
            return text
            
        words = text.split()
        last_person = None
        last_org = None
        
        for ent in reversed(context_entities):
            if ent['label'] == 'PERSON' and not last_person:
                last_person = ent['text']
            elif ent['label'] in ['ORG', 'PRODUCT', 'GPE'] and not last_org:
                last_org = ent['text']
                
        for i, word in enumerate(words):
            word_lower = re.sub(r'[^a-zA-Z]', '', word.lower())
            if word_lower in ['he', 'him', 'his', 'she', 'her', 'hers'] and last_person:
                # Basic exact replacement (case sensitive wrapper)
                words[i] = words[i].replace(word, last_person)
            elif word_lower in ['it', 'its'] and last_org:
                words[i] = words[i].replace(word, last_org)
                
        return " ".join(words)

resolver = CoreferenceResolver()

def resolve_coreferences(text: str, context_entities: list):
    return resolver.resolve(text, context_entities)
