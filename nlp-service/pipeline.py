import spacy
import nltk
from nltk.corpus import wordnet
from nltk.wsd import lesk
from gensim.models import Word2Vec
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Any, Dict, Iterable, List, Optional

try:
    import neuralcoref
except ImportError:  # pragma: no cover
    neuralcoref = None

nltk_packages = ['punkt', 'wordnet', 'omw-1.4', 'averaged_perceptron_tagger']
for package in nltk_packages:
    nltk.download(package, quiet=True)


class NLPPipeline:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        if neuralcoref:
            neuralcoref.add_to_pipe(self.nlp)
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=100)

    def _token_info(self, doc):
        return [token for token in doc if not token.is_space]

    def _extract_entities(self, doc):
        return [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]

    def _dependency_snapshot(self, doc):
        return [
            {'text': token.text, 'dep': token.dep_, 'head': token.head.text}
            for token in doc if token.head
        ]

    def _compose_reply(self, message: str, tokens: List[str], keywords: List[str]) -> str:
        topic = tokens[0] if tokens else 'that topic'
        gist = keywords[0] if keywords else 'your context'
        keyword_snippet = ', '.join(keywords[:3]) if keywords else gist
        return f'I tracked {len(tokens)} tokens around {topic!r} and highlighted {keyword_snippet}.'

    def _context_keywords(self, context: List[str]) -> List[str]:
        if len(context) < 2:
            return []
        truncated = context[-5:]
        matrix = self.vectorizer.fit_transform(truncated)
        scores = matrix.sum(axis=0).A1
        terms = self.vectorizer.get_feature_names_out()
        ranked = sorted(zip(scores, terms), reverse=True)
        return [term for score, term in ranked if score > 0][:5]

    def _compute_wsd(self, doc):
        pos_map = {'NOUN': 'n', 'VERB': 'v', 'ADJ': 'a', 'ADV': 'r'}
        results: Dict[str, Optional[str]] = {}
        for token in doc:
            if not token.is_alpha or token.is_stop:
                continue
            sense = lesk(doc.text.split(), token.text, pos_map.get(token.pos_, None))
            if sense:
                results[token.text] = sense.definition()
            else:
                synsets = wordnet.synsets(token.text.lower())
                results[token.text] = synsets[0].definition() if synsets else None
        return results

    def _coref_clusters(self, doc):
        if neuralcoref and hasattr(doc._, 'coref_clusters') and doc._.coref_clusters:
            return [cluster.main.text for cluster in doc._.coref_clusters]
        pronouns = [token.text for token in doc if token.pos_ == 'PRON']
        entities = [ent.text for ent in doc.ents]
        return pronouns[:3] + entities[:3]

    def _train_embeddings(self, doc, context: Iterable[str]):
        sentences = [list(context)]
        sentences.append([token.lemma_.lower() for token in doc if token.is_alpha])
        try:
            model = Word2Vec(sentences, vector_size=100, window=3, min_count=1, epochs=12)
            return {
                token.text: model.wv[token.text.lower()].tolist()
                for token in doc
                if token.text.lower() in model.wv
            }
        except Exception:
            return {}

    def _build_ngrams(self, tokens: List[str], n: int = 2):
        if len(tokens) < n:
            return {}
        counts: Dict[str, int] = {}
        for i in range(len(tokens) - n + 1):
            gram = ' '.join(tokens[i : i + n]).lower()
            counts[gram] = counts.get(gram, 0) + 1
        total = sum(counts.values())
        vocab = len(counts)
        return {gram: (count + 1) / (total + vocab) for gram, count in counts.items()}

    def _memory_summary(self, context: List[str]) -> str:
        if not context:
            return 'No history yet.'
        recent = context[-3:]
        return ' :: '.join(recent)

    def process(self, message: str, context: Optional[List[Dict[str, Any]]] = None):
        if not message:
            raise ValueError('Message text is required')
        doc = self.nlp(message)
        tokens = [token.text for token in self._token_info(doc)]
        lemmas = [token.lemma_ for token in self._token_info(doc)]
        context_texts = [item.get('text', '') for item in (context or []) if item.get('text')]
        keywords = self._context_keywords(context_texts + [message])
        analysis = {
            'reply': self._compose_reply(message, tokens, keywords),
            'tokens': tokens,
            'lemmas': lemmas,
            'entities': self._extract_entities(doc),
            'dependencies': self._dependency_snapshot(doc),
            'wsd': self._compute_wsd(doc),
            'coreferences': self._coref_clusters(doc),
            'embeddings': self._train_embeddings(doc, context_texts),
            'ngrams': self._build_ngrams(tokens),
            'contextSummary': self._memory_summary(context_texts),
            'keywords': keywords,
        }
        return analysis
