import nltk
from nltk.wsd import lesk
from nltk.tokenize import word_tokenize

def setup_nltk():
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet', quiet=True)

setup_nltk()

def disambiguate_word_sense(text: str, ambiguous_word: str):
    """Word Sense Disambiguation using Lesk algorithm."""
    tokens = word_tokenize(text)
    synset = lesk(tokens, ambiguous_word)
    if synset:
        return {"synset": synset.name(), "definition": synset.definition()}
    return None
