from pipeline import NLPPipeline

def test_pipeline_returns_structure():
    pipeline = NLPPipeline()
    analysis = pipeline.process('Share a quick summary of natural language processing.', context=[{'text': 'Earlier context', 'role': 'user'}])
    assert 'reply' in analysis
    assert isinstance(analysis['tokens'], list)
    assert isinstance(analysis['entities'], list)
    assert isinstance(analysis['ngrams'], dict)
