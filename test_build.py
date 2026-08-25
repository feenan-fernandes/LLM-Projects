
import requests, json

payload = {
    'prompt': 'Write a hello world script in Python named test_hello.py',
    'uncensored': False,
    'files': [],
    'history': []
}
try:
    with requests.post('http://127.0.0.1:5000/build', json=payload, stream=True) as r:
        for line in r.iter_lines():
            if line:
                data = json.loads(line.decode('utf-8'))
                print(f"[Iteration {data.get('iteration', '?')}] Type: {data.get('type')} | Action: {data.get('action')} | Status: {data.get('status')} ")
except Exception as e:
    print('Failed to test:', e)

