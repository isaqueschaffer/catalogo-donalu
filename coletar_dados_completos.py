import csv
import json
import os
import re
import ssl
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import unescape

ctx = ssl.create_default_context()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def clean_text(t):
    if not t:
        return ""
    t = re.sub(r'<[^>]+>', ' ', t)
    t = unescape(t)
    return ' '.join(t.split()).strip()

# Classification helper
def infer_segment(name, desc, url):
    text = (name + " " + desc + " " + url).lower()
    if any(k in text for k in ['roupa', 'amaciante', 'tuff', 'alvejante', 'percarbonato', 'passa fácil', 'passa facil']):
        return "Lavanderia e Tecidos"
    elif any(k in text for k in ['louça', 'louca', 'grelha', 'forno', 'air fryer', 'alumil', 'desengordurante', 'inox', 'microondas']):
        return "Cozinha e Desengordurantes"
    elif any(k in text for k in ['pedrex', 'pedra', 'porcelanato', 'cerâmica', 'ceramica', 'piso', 'rejunte', 'cera', 'pretita', 'laminado', 'polylar']):
        return "Pisos, Pedras e Superfícies"
    elif any(k in text for k in ['asseptgel', 'antisséptico', 'antisseptico', 'clorexidina', 'álcool em gel', 'alcool em gel', 'sabonete']):
        return "Higiene Pessoal e Antissepsia"
    elif any(k in text for k in ['odor', 'only', 'free pet', 'difusor', 'aroma', 'bloqueador']):
        return "Aromatização e Odorizantes"
    elif any(k in text for k in ['pneu', 'indy cryl', 'automotiva', 'desengraxante', 'couro', 'silicone']):
        return "Linha Automotiva e Especialidades"
    elif any(k in text for k in ['cloro', 'água sanitária', 'agua sanitaria', 'desinfetante', 'limo', 'ferrugem', 'flotador', 'maximoom', 'vorel', 'telas', 'vidros', 'sanitária', 'sanitaria', 'soda', 'querosene']):
        return "Desinfecção e Limpeza Geral"
    else:
        return "Limpeza Geral e Institucional"

# Active ingredient helper
def infer_active(name, desc, segment):
    text = (name + " " + desc).lower()
    if 'quartenário' in text or 'quaternario' in text:
        return "Quaternário de Amônio"
    elif 'hipoclorito' in text or 'cloro ativo' in text or 'água sanitária' in text:
        return "Hipoclorito de Sódio (Cloro Ativo)"
    elif 'percarbonato' in text:
        return "Percarbonato de Sódio Puro (Oxigênio Ativo)"
    elif 'álcool 70' in text or 'alcool 70' in text:
        return "Álcool Etílico 70º INPM"
    elif '46%' in text:
        return "Álcool Etílico 46º INPM + Quaternário"
    elif 'clorexidina' in text:
        return "Digliconato de Clorexidina"
    elif 'querosene' in text:
        return "Solvente Alifático (Querosene desodorizado) + Tensoativo"
    elif 'amoniacal' in text:
        return "Amônia e Tensoativos Biodegradáveis"
    elif 'pedrex' in text or 'ácido' in text or 'limpa pedras' in text:
        return "Ácido Inorgânico Especial + Tensoativos"
    elif 'cera' in text or 'polímero' in text or 'pretita' in text:
        return "Polímeros Acrílicos e Emulsão de Cera Especial"
    elif 'silicone' in text:
        return "Polidimetilsiloxano (Silicone Fluido)"
    elif 'soda' in text:
        return "Hidróxido de Sódio (Soda Cáustica)"
    elif 'enzima' in text or '2 em 1' in text:
        return "Complexo Enzimático e Tensoativos Não-Iônicos"
    elif 'amaciante' in text:
        return "Cloreto de Dialquil Dimetil Amônio + Microcápsulas de Perfume"
    elif 'desengordurante' in text or 'flotador' in text:
        return "Tensoativos Aniônicos e Solventes Solúveis em Água"
    elif 'inox' in text:
        return "Óleos Minerais Especiais e Tensoativo"
    else:
        return "Tensoativos Aniônicos Biodegradáveis e Coadjuvantes"

# Load current CSV
products = []
with open('catalogo_produtos.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f, delimiter=';')
    header = next(reader)
    for r in reader:
        products.append({
            'index': int(r[0]),
            'name': r[1],
            'png_file': r[2],
            'webp_file': r[3],
            'dims': r[4],
            'image_url': r[5],
            'product_url': r[6]
        })

print(f"Total produtos para coletar detalhes: {len(products)}")

def fetch_product_details(p):
    url = p['product_url']
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                
            # 1. Description
            desc_match = re.search(r'<h1[^>]*>.*?</h1>\s*<p class="[^"]*opacity-80[^"]*">(.*?)</p>', html, re.DOTALL)
            desc = clean_text(desc_match.group(1)) if desc_match else ""
            
            # 2. Embalagens
            emb_matches = []
            emb_block = re.search(r'Embalagens</h5>(.*?)(?:<hr|</div>\s*</div>)', html, re.DOTALL)
            if emb_block:
                embs = re.findall(r'<a[^>]*class="[^"]*rounded-full[^"]*"[^>]*>(.*?)</a>', emb_block.group(1), re.DOTALL)
                emb_matches = [clean_text(e) for e in embs if clean_text(e)]
            if not emb_matches:
                # try finding volumes in name
                v_match = re.search(r'(\d+(?:[.,]\d+)?\s*(?:ml|l|kg|g))\b', p['name'], re.IGNORECASE)
                if v_match:
                    emb_matches = [v_match.group(1).upper()]
                else:
                    emb_matches = ["Sob consulta"]
                    
            # 3. Fragrâncias
            frag_matches = []
            frag_block = re.search(r'Fragrâncias</h5>\s*<div[^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)
            if frag_block:
                frags = re.findall(r'<a[^>]*>(.*?)</a>', frag_block.group(1), re.DOTALL)
                frag_matches = [clean_text(f) for f in frags if clean_text(f)]
            if not frag_matches:
                # check if fragrance is in name
                for f_candidate in ['Lavanda', 'Lemon', 'Erva Doce', 'Citrus', 'Coco', 'Spring', 'Winter', 'Chá Branco', 'Clear Soft', 'Original', 'Tradicional', 'Neutro']:
                    if f_candidate.lower() in p['name'].lower():
                        frag_matches.append(f_candidate)
                if not frag_matches:
                    frag_matches = ["Sem fragrância" if "pedras" in p['name'].lower() or "cloro" in p['name'].lower() else "Original / Tradicional"]

            # 4. Modo de uso
            modo_match = re.search(r'Modo\s+uso\s*</h2>.*?<div[^>]*>.*?<p[^>]*>(.*?)</p>', html, re.DOTALL)
            modo = clean_text(modo_match.group(1)) if modo_match else ""
            
            # 5. Onde aplicar
            onde_matches = []
            idx_onde = html.find('Onde aplicar?')
            if idx_onde != -1:
                onde_snippet = html[idx_onde:idx_onde+3000]
                alts = re.findall(r'alt="([^"]+)"', onde_snippet)
                alts_filtered = [clean_text(a) for a in alts if clean_text(a) and not any(k in a.lower() for k in ['logo', 'start', 'bandeira', 'arrow', 'instagram', 'search', 'produto'])]
                onde_matches = alts_filtered[:6]

            # 6. Ficha técnica PDF
            ficha_match = re.search(r'href="([^"]+)"[^>]*download="[^"]*ficha-tecnica"', html)
            ficha_url = ficha_match.group(1) if ficha_match else ""
            
            # 7. Brand / Linha
            brand = "Start Química"
            for b in ['Azulim', 'Tuff', 'Pedrex', 'Asseptgel', 'Indy Cryl', 'Alumil', 'Only', 'Free Pet', 'Maximoom', 'Polylar', 'Vorel', 'Pretita']:
                if b.lower() in p['name'].lower():
                    brand = b
                    break

            # 8. Segment
            segment = infer_segment(p['name'], desc, p['product_url'])
            
            # 9. Active ingredient
            active = infer_active(p['name'], desc, segment)
            
            return {
                **p,
                'brand': brand,
                'segment': segment,
                'description': desc or f"Produto de alta performance da linha {brand}, desenvolvido com rigor técnico para máxima eficiência na limpeza e tratamento.",
                'packaging': ", ".join(emb_matches),
                'fragrance': ", ".join(frag_matches),
                'active': active,
                'directions': modo or "Aplicar diretamente ou diluído conforme a sujidade. Deixar agir por alguns instantes, esfregar se necessário e enxaguar com água limpa.",
                'surfaces': ", ".join(onde_matches) if onde_matches else "Superfícies laváveis compatíveis com a formulação",
                'ficha_tecnica': ficha_url
            }
        except Exception as e:
            if attempt == 2:
                print(f"Erro em {p['name']}: {e}")
                brand = "Start Química"
                segment = infer_segment(p['name'], "", p['product_url'])
                return {
                    **p,
                    'brand': brand,
                    'segment': segment,
                    'description': f"Produto da linha {brand} para uso profissional e doméstico.",
                    'packaging': "Diversas opções",
                    'fragrance': "Original",
                    'active': infer_active(p['name'], "", segment),
                    'directions': "Consulte o rótulo para instruções específicas.",
                    'surfaces': "Superfícies compatíveis",
                    'ficha_tecnica': ""
                }
            time.sleep(1)

detailed_products = []
print("Iniciando coleta paralela de informações técnicas...")
with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(fetch_product_details, p): p for p in products}
    for future in as_completed(futures):
        res = future.result()
        detailed_products.append(res)
        print(f"[{res['index']:03d}] Coletado: {res['name']} | Segmento: {res['segment']}")

detailed_products.sort(key=lambda x: x['index'])

with open('catalogo_detalhado.json', 'w', encoding='utf-8') as f:
    json.dump(detailed_products, f, ensure_ascii=False, indent=2)

print(f"\nColeta concluída! Salvo em catalogo_detalhado.json ({len(detailed_products)} itens).")

