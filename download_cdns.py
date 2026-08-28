import os
import urllib.request

os.makedirs('static/js', exist_ok=True)

urls = {
    'tailwindcss.js': 'https://cdn.tailwindcss.com',
    'react.development.js': 'https://unpkg.com/react@18/umd/react.development.js',
    'react-dom.development.js': 'https://unpkg.com/react-dom@18/umd/react-dom.development.js',
    'babel.min.js': 'https://unpkg.com/@babel/standalone/babel.min.js',
    'marked.min.js': 'https://cdn.jsdelivr.net/npm/marked/marked.min.js'
}

for name, url in urls.items():
    path = f'static/js/{name}'
    if not os.path.exists(path):
        print(f"Downloading {name}...")
        try:
            # add user agent to avoid 403 on some CDNs
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(path, 'wb') as out_file:
                out_file.write(response.read())
        except Exception as e:
            print(f"Failed to download {name}: {e}")
    else:
        print(f"{name} already exists.")
