import json, urllib.request

tests = [
    "how to learn machine learning",
    "best interview tips",
    "I feel sad today",
    "how to sleep better", 
    "what is artificial intelligence",
    "recommend some good books",
    "best deals on phones",
    "how to stay safe online",
    "hello",
    "goodbye",
    "how to lose weight",
    "what is python programming",
    "tips for resume writing",
]

with open('_test_out.txt', 'w', encoding='utf-8') as f:
    for msg in tests:
        data = json.dumps({"message": msg, "level": 3}).encode('utf-8')
        req = urllib.request.Request(
            "http://127.0.0.1:8001/chat",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read().decode('utf-8'))
        f.write(f"Q: {msg}\n")
        f.write(f"Intent: {result.get('intent','?')} | Score: {result.get('similarity_score',0):.2f}\n")
        f.write(f"A: {result['reply']}\n\n")
print("Done - see _test_out.txt")
