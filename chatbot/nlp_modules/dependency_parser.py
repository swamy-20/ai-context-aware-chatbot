import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    pass # Managed by lemmatizer

def parse_dependencies(text: str):
    """Dependency parsing using spaCy."""
    if not text:
        return []
    doc = nlp(text)
    dependencies = [{"token": token.text, "dep": token.dep_, "head": token.head.text} for token in doc]
    return dependencies
