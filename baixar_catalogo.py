import os
import re
import ssl
import csv
import io
import time
import html as html_lib
import urllib.request
import unicodedata
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
BASE_URL = "https://www.startquimica.com.br"
TARGET_COUNT = 80
OUTPUT_DIR_PNG = "imagens_produtos"
OUTPUT_DIR_WEBP = os.path.join(OUTPUT_DIR_PNG, "originais_webp")
CSV_PATH = "catalogo_produtos.csv"
HTML_GALLERY_PATH = "catalogo_visual.html"

os.makedirs(OUTPUT_DIR_PNG, exist_ok=True)
os.makedirs(OUTPUT_DIR_WEBP, exist_ok=True)

ctx = ssl.create_default_context()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def sanitize_filename(name):
    # Unescape HTML entities (e.g. &amp; -> &)
    name = html_lib.unescape(name)
    # Replace forbidden Windows characters: \ / : * ? " < > |
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    # Normalize multiple whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def fetch_page(page_num):
    url = f"{BASE_URL}/pt-BR/produtos?page={page_num}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            cards = re.findall(
                r'<a\s+href="([^"]+)"\s+class="block">.*?<img[^>]+src="([^"]+)".*?<div class="text-center text-base font-semibold font-bricolage text-\[#003ca5\]">\s*([^<]+?)\s*</div>',
                html,
                re.DOTALL
            )
            return cards
    except Exception as e:
        print(f"Erro ao buscar página {page_num}: {e}")
        return []

print(f"--- 1. Coletando lista de produtos do catálogo da Start Química ---")
products = []
seen_images = set()
page = 1

while len(products) < TARGET_COUNT and page <= 20:
    print(f"Buscando página {page}...")
    cards = fetch_page(page)
    if not cards:
        print(f"Nenhum card retornado na página {page}.")
        break
    
    for prod_url, img_url, name in cards:
        name_clean = sanitize_filename(' '.join(name.strip().split()))
        
        # Verify valid product image
        if img_url in seen_images:
            continue
        
        # Ensure it is a valid PIM product image
        if "storage" not in img_url:
            continue
            
        seen_images.add(img_url)
        idx = len(products) + 1
        
        # Format filename: e.g. "001 - Limpa Pedras Pedrex"
        base_name = f"{idx:03d} - {name_clean}"
        
        products.append({
            'index': idx,
            'name': name_clean,
            'base_name': base_name,
            'product_url': prod_url if prod_url.startswith('http') else BASE_URL + prod_url,
            'image_url': img_url if img_url.startswith('http') else BASE_URL + img_url,
            'png_file': f"{base_name}.png",
            'webp_file': f"{base_name}.webp"
        })
        
        if len(products) == TARGET_COUNT:
            break
            
    page += 1

print(f"\nTotal de produtos selecionados: {len(products)}")

print(f"\n--- 2. Baixando e processando {len(products)} imagens em alta qualidade ---")

def download_and_process(item):
    img_url = item['image_url']
    png_path = os.path.join(OUTPUT_DIR_PNG, item['png_file'])
    webp_path = os.path.join(OUTPUT_DIR_WEBP, item['webp_file'])
    
    req = urllib.request.Request(img_url, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=25) as resp:
                raw_bytes = resp.read()
                
            # Save original webp
            with open(webp_path, 'wb') as f:
                f.write(raw_bytes)
                
            # Process with PIL to ensure consistent PNG format with transparency
            img = Image.open(io.BytesIO(raw_bytes))
            # Convert to RGBA if not already
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
                
            # Save as optimized PNG with transparent background
            img.save(png_path, format='PNG', optimize=True)
            
            return {
                'index': item['index'],
                'success': True,
                'name': item['name'],
                'size': img.size,
                'mode': img.mode,
                'file_size_kb': round(len(raw_bytes) / 1024, 1)
            }
        except Exception as e:
            if attempt == 2:
                return {
                    'index': item['index'],
                    'success': False,
                    'name': item['name'],
                    'error': str(e)
                }
            time.sleep(1)

results = []
with ThreadPoolExecutor(max_workers=6) as executor:
    futures = {executor.submit(download_and_process, p): p for p in products}
    for future in as_completed(futures):
        res = future.result()
        results.append(res)
        status = "OK" if res['success'] else "FALHA"
        dim = f"{res.get('size')}" if res['success'] else res.get('error')
        print(f"[{res['index']:03d}/{TARGET_COUNT}] {status}: {res['name']} ({dim})")

results.sort(key=lambda x: x['index'])
success_count = sum(1 for r in results if r['success'])
print(f"\nDownload concluído: {success_count}/{TARGET_COUNT} imagens processadas com sucesso.")

print(f"\n--- 3. Gerando catálogo em CSV (catalogo_produtos.csv) ---")
with open(CSV_PATH, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow([
        'Item',
        'Nome do Produto',
        'Arquivo PNG (Fundo Transparente)',
        'Arquivo WEBP Original',
        'Dimensões',
        'URL da Imagem Oficial',
        'Link do Produto no Site'
    ])
    for p, r in zip(products, results):
        dim = f"{r.get('size', ('N/A','N/A'))[0]}x{r.get('size', ('N/A','N/A'))[1]}" if r.get('success') else 'Erro'
        writer.writerow([
            p['index'],
            p['name'],
            p['png_file'],
            p['webp_file'],
            dim,
            p['image_url'],
            p['product_url']
        ])
print(f"Planilha CSV gerada com sucesso: {CSV_PATH}")

print(f"\n--- 4. Gerando galeria visual interativa (catalogo_visual.html) ---")
html_cards = []
for p in products:
    relative_png = f"{OUTPUT_DIR_PNG}/{p['png_file'].replace('%', '%25')}"
    html_cards.append(f"""
        <div class="card">
            <div class="badge">#{p['index']:02d}</div>
            <div class="img-box">
                <img src="{relative_png}" alt="{p['name']}" loading="lazy">
            </div>
            <div class="card-body">
                <h3>{p['name']}</h3>
                <a href="{p['product_url']}" target="_blank" class="link-btn">Ver na Start Química &rarr;</a>
            </div>
        </div>
    """)

html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo Start Química - 80 Produtos</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
        body {{ background-color: #f4f6f9; color: #1e293b; padding: 30px 20px; }}
        .header {{ max-width: 1300px; margin: 0 auto 30px auto; text-align: center; }}
        .header h1 {{ font-size: 28px; color: #003ca5; margin-bottom: 8px; font-weight: 800; }}
        .header p {{ color: #64748b; font-size: 15px; }}
        .stats {{ display: flex; justify-content: center; gap: 20px; margin-top: 15px; font-size: 14px; color: #334155; }}
        .stat-item {{ background: #fff; padding: 6px 16px; border-radius: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); font-weight: 600; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; max-width: 1300px; margin: 0 auto; }}
        .card {{ background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s, box-shadow 0.2s; position: relative; }}
        .card:hover {{ transform: translateY(-4px); box-shadow: 0 10px 20px rgba(0, 60, 165, 0.1); border-color: #cbd5e1; }}
        .badge {{ position: absolute; top: 12px; left: 12px; background: #003ca5; color: #fff; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 6px; z-index: 2; }}
        .img-box {{ height: 230px; display: flex; align-items: center; justify-content: center; padding: 20px; background: radial-gradient(circle, #f8fafc 0%, #edf2f7 100%); border-bottom: 1px solid #f1f5f9; }}
        .img-box img {{ max-height: 100%; max-width: 100%; object-fit: contain; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.06)); }}
        .card-body {{ padding: 16px; flex: 1; display: flex; flex-direction: column; justify-content: space-between; }}
        .card-body h3 {{ font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 12px; line-height: 1.4; }}
        .link-btn {{ display: inline-block; text-align: center; font-size: 12px; font-weight: 600; color: #003ca5; text-decoration: none; padding: 7px 10px; border-radius: 6px; background: #eff6ff; transition: background 0.2s; }}
        .link-btn:hover {{ background: #dbeafe; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Catálogo de Produtos - Start Química</h1>
        <p>Seleção de 80 produtos com imagens oficiais em alta qualidade para confecção de catálogo.</p>
        <div class="stats">
            <div class="stat-item">📦 Total: {len(products)} Produtos</div>
            <div class="stat-item">🖼️ Formato: PNG Transparente + WEBP Original</div>
            <div class="stat-item">✨ Fundo: Transparente (Studio PIM)</div>
        </div>
    </div>
    <div class="grid">
        {''.join(html_cards)}
    </div>
</body>
</html>
"""

with open(HTML_GALLERY_PATH, 'w', encoding='utf-8') as f:
    f.write(html_content)
print(f"Galeria visual HTML gerada com sucesso: {HTML_GALLERY_PATH}")

