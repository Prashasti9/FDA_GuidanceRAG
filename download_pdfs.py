import requests
import os

urls_file = "pdf_links.txt"
output_dir = "corpus"

os.makedirs(output_dir, exist_ok=True)

with open(urls_file) as f:
    urls = [line.strip() for line in f if line.strip()]

headers = {"User-Agent": "Mozilla/5.0"}

for url in urls:
    media_id = url.rstrip("/").split("/")[-2]
    filename = f"fda_{media_id}.pdf"
    filepath = os.path.join(output_dir, filename)
    if os.path.exists(filepath):
        print(f"Skipping (already downloaded): {filename}")
        continue
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        with open(filepath, "wb") as out:
            out.write(resp.content)
        print(f"Downloaded: {filename}")
    except Exception as e:
        print(f"FAILED: {url} ({e})")

print(f"\nDone. {len(urls)} URLs processed.")
