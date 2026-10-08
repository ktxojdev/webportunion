with open('C:/Users/ktxoj1/.gemini/antigravity/brain/6e9be547-fd64-4af3-87a0-ce9d0c2ec509/.system_generated/steps/2374/content.md', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'Remarkable-Net6962', text)]
print(f"Total mentions of Remarkable-Net6962: {len(matches)}")
for idx in matches[:5]:
    snippet = text[max(0, idx-100):min(len(text), idx+500)]
    # clean HTML tags
    clean = re.sub(r'<[^>]+>', ' ', snippet)
    clean = ' '.join(clean.split())
    print("\n--- COMMENT ---")
    print(clean.encode('ascii', errors='replace').decode('ascii'))
