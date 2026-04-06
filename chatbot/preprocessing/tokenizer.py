import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import os

# Ensure NLTK resources are available
def setup_nltk():
    resources = ['punkt', 'stopwords', 'punkt_tab']
    for res in resources:
        try:
            nltk.data.find(f'tokenizers/{res}' if 'punkt' in res else f'corpora/{res}')
        except LookupError:
            nltk.download(res, quiet=True)

setup_nltk()
stop_words = set(stopwords.words('english'))

def tokenize_text(text: str):
    """Tokenize text and remove stopwords/punctuation."""
    if not text:
        return [], []
    text = text.lower()
    # Tokenize
    tokens = word_tokenize(text)
    # Remove stopwords and punctuation
    clean_tokens = [t for t in tokens if t not in stop_words and t not in string.punctuation]
    return tokens, clean_tokens
