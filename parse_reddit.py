import re, json

with open('C:/Users/ktxoj1/.gemini/antigravity/brain/6e9be547-fd64-4af3-87a0-ce9d0c2ec509/.system_generated/steps/2374/content.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Find JSON-LD script blocks
blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', text, re.DOTALL)
for b in blocks:
    try:
        data = json.loads(b)
        print("JSON-LD found! Type:", data.get('@type'))
        if 'comment' in data:
            for c in data['comment']:
                author = c.get('author', {}).get('name', 'unknown')
                txt = c.get('text', '')
                print(f"[{author}]: {txt}")
    except Exception as e:
        pass

# Also grep for any mentions of discord, wasm, github, etc.
for line in text.splitlines():
    if any(k in line.lower() for k in ['discord.gg', 'github.com', 'dx11', 'd3d11', 'webgl', 'porting']):
        # strip tags
        clean = re.sub(r'<[^>]+>', ' ', line)
        clean = ' '.join(clean.split())
        if len(clean) > 20:
            print("MATCH:", clean[:160].encode('ascii', errors='replace').decode('ascii'))
