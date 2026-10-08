import re, json

with open('C:/Users/ktxoj1/.gemini/antigravity/brain/6e9be547-fd64-4af3-87a0-ce9d0c2ec509/.system_generated/steps/2374/content.md', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = r'\"name\":\"Remarkable-Net6962\"[^\}]*\}.*?\"text\":\"([^\"]+)\"'
matches = re.findall(pattern, text)
print(f"Found {len(matches)} replies by Remarkable-Net6962:")
for i, m in enumerate(matches):
    print(f"\n[{i+1}]: {m.encode('ascii', errors='replace').decode('ascii')}")
