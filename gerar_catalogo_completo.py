import json
import os
import re

with open('catalogo_detalhado.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

# Segment styles
SEGMENT_STYLES = {
    "Pisos, Pedras e Tratamento de Superfícies": {
        "icon": "🏛️",
        "bg": "#fefce8",
        "text": "#854d0e",
        "border": "#fef08a",
        "color": "#b45309",
        "short": "Pisos & Pedras",
        "desc": "Soluções especializadas para tratamento, proteção, restauração e acabamento de pisos nobres, cerâmicas, porcelanatos e pedras rústicas."
    },
    "Desinfecção e Limpeza Geral Multiuso": {
        "icon": "✨",
        "bg": "#ecfeff",
        "text": "#0e7490",
        "border": "#a5f3fc",
        "color": "#0284c7",
        "short": "Limpeza Geral",
        "desc": "Alta eficácia contra germes e bactérias aliada ao poder desengraxante e desengordurante para superfícies em ambientes domésticos e comerciais."
    },
    "Lavanderia e Tratamento de Roupas": {
        "icon": "🧺",
        "bg": "#eef2ff",
        "text": "#4338ca",
        "border": "#c7d2fe",
        "color": "#4f46e5",
        "short": "Lavanderia",
        "desc": "Fórmulas de alta tecnologia com enzimas ativas, oxigênio puro e microcápsulas de perfume para o cuidado e conservação de tecidos."
    },
    "Cozinha e Tratamento de Metais": {
        "icon": "🍳",
        "bg": "#fff7ed",
        "text": "#c2410c",
        "border": "#fed7aa",
        "color": "#ea580c",
        "short": "Cozinha & Metais",
        "desc": "Poder desengordurante instantâneo, remoção de crostas e gorduras pesadas, polimento e restauração de inox e alumínio."
    },
    "Higiene Pessoal e Antissepsia": {
        "icon": "🧴",
        "bg": "#f0fdf4",
        "text": "#15803d",
        "border": "#bbf7d0",
        "color": "#16a34a",
        "short": "Higiene Pessoal",
        "desc": "Linha Asseptgel com eficácia bactericida comprovada, álcool 70º INPM hidratante, sabonetes antissépticos e proteção contínua para a pele."
    },
    "Automotivo e Oficinas": {
        "icon": "🚗",
        "bg": "#f1f5f9",
        "text": "#334155",
        "border": "#cbd5e1",
        "color": "#1e293b",
        "short": "Linha Automotiva",
        "desc": "Produtos de estética automotiva profissional: revitalização de pneus, hidratação de couros, ceras de alto brilho e pastas desengraxantes."
    },
    "Aromatização e Cuidados Pet": {
        "icon": "🌸",
        "bg": "#fdf4ff",
        "text": "#a21caf",
        "border": "#f5d0fe",
        "color": "#c026d3",
        "short": "Aromatizantes & Pet",
        "desc": "Fragrâncias finas e neutralizadores biológicos de odores para transformar ambientes residenciais e espaços de convivência com animais de estimação."
    }
}

# Group products by segment
by_segment = {}
for p in products:
    seg = p['segment']
    if seg not in by_segment:
        by_segment[seg] = []
    by_segment[seg].append(p)

# Generate HTML for product cards
def render_product_card(p):
    # Safe relative image path for HTML URL
    # Replace % with %25 for safe browser URI parsing
    safe_png = f"imagens_produtos/{p['png_file'].replace('%', '%25')}"
    seg_info = SEGMENT_STYLES.get(p['segment'], {
        "icon": "📦", "bg": "#f8fafc", "text": "#334155", "border": "#e2e8f0", "color": "#003ca5"
    })
    
    # Packaging badges
    pkg_list = [x.strip() for x in p['packaging'].split(',') if x.strip()]
    pkg_badges = "".join([f'<span class="spec-pill pkg-pill">{pkg}</span>' for pkg in pkg_list])
    
    # Fragrance badges
    frag_list = [x.strip() for x in p['fragrance'].split(',') if x.strip()]
    frag_badges = "".join([f'<span class="spec-pill frag-pill"><span class="pill-icon">🌸</span> {f}</span>' for f in frag_list])
    
    # Surfaces tag
    surfaces = p.get('surfaces', '')
    surf_html = f'<div class="card-spec-row"><span class="spec-label">Onde usar:</span> <span class="spec-val">{surfaces}</span></div>' if surfaces else ''
    
    ficha_btn = f'<a href="{p["product_url"]}" target="_blank" class="btn-site">Ficha Técnica &rarr;</a>'
    
    return f"""
    <div class="product-card" 
         data-id="{p['index']}" 
         data-segment="{p['segment']}" 
         data-name="{p['name'].lower()}" 
         data-active="{p['active'].lower()}" 
         data-fragrance="{p['fragrance'].lower()}">
        
        <div class="card-top-bar">
            <span class="card-sku">#{p['index']:03d}</span>
            <span class="card-segment-tag" style="background:{seg_info['bg']}; color:{seg_info['text']}; border-color:{seg_info['border']};">
                {seg_info['icon']} {seg_info['short']}
            </span>
            <button class="feedback-mark-btn" onclick="toggleApproval({p['index']})" title="Marcar status / Feedback" id="btn-status-{p['index']}">
                ⚪
            </button>
        </div>

        <div class="card-img-container">
            <img src="{safe_png}" alt="{p['name']}" loading="lazy" class="card-img" onerror="this.onerror=null; this.src='{safe_png.replace('%25', '%')}';">
            <div class="card-brand-badge">{p['brand']}</div>
        </div>

        <div class="card-content">
            <h3 class="product-title">{p['name']}</h3>
            
            <p class="product-desc">{p['description']}</p>
            
            <div class="spec-section">
                <div class="card-spec-row">
                    <span class="spec-label">Embalagens:</span>
                    <div class="pills-wrap">{pkg_badges}</div>
                </div>

                <div class="card-spec-row">
                    <span class="spec-label">Fragrância:</span>
                    <div class="pills-wrap">{frag_badges}</div>
                </div>

                <div class="card-spec-row active-substance">
                    <span class="spec-label">Ativo Principal:</span>
                    <span class="spec-val active-val">🧪 {p['active']}</span>
                </div>

                <div class="card-spec-row directions-row">
                    <span class="spec-label">Indicação:</span>
                    <span class="spec-val directions-val">{p['directions']}</span>
                </div>
                
                {surf_html}
            </div>

            <div class="card-footer">
                {ficha_btn}
                <button class="btn-comment" onclick="openCommentModal({p['index']})">💬 Palpite / Ajuste</button>
            </div>
        </div>
    </div>
    """

# Generate sections by segment
segments_html = []
toc_items = []

for seg_name, p_list in by_segment.items():
    seg_info = SEGMENT_STYLES[seg_name]
    anchor_id = "sec-" + re.sub(r'[^a-zA-Z0-9]', '', seg_name).lower()
    
    toc_items.append(f"""
        <a href="#{anchor_id}" class="toc-card">
            <div class="toc-icon" style="background:{seg_info['bg']}; color:{seg_info['text']};">{seg_info['icon']}</div>
            <div class="toc-info">
                <h4>{seg_name}</h4>
                <p>{len(p_list)} produtos certificados</p>
            </div>
            <span class="toc-arrow">&rarr;</span>
        </a>
    """)
    
    cards_html = "\n".join([render_product_card(p) for p in p_list])
    
    segments_html.append(f"""
    <section class="segment-section" id="{anchor_id}">
        <div class="segment-header" style="border-left: 6px solid {seg_info['color']};">
            <div class="seg-title-row">
                <span class="seg-badge" style="background:{seg_info['bg']}; color:{seg_info['text']}; border: 1px solid {seg_info['border']};">
                    {seg_info['icon']} {seg_name}
                </span>
                <span class="seg-count">{len(p_list)} itens</span>
            </div>
            <h2 class="seg-heading">{seg_name}</h2>
            <p class="seg-desc">{seg_info['desc']}</p>
        </div>
        
        <div class="products-grid">
            {cards_html}
        </div>
    </section>
    """)

# Combine everything into complete HTML
full_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo Oficial de Produtos - Start Química | Portfólio Completo</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Bricolage+Grotesque:opsz,wght@12..96,400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        /* === DESIGN SYSTEM & RESET === */
        :root {{
            --primary: #003ca5;
            --primary-dark: #002266;
            --primary-light: #1e60d5;
            --navy-deep: #03122c;
            --accent-gold: #d97706;
            --accent-gold-light: #fef3c7;
            --bg-page: #f8fafc;
            --surface-white: #ffffff;
            --text-dark: #0f172a;
            --text-muted: #64748b;
            --text-light: #94a3b8;
            --border-light: #e2e8f0;
            --border-hover: #cbd5e1;
            --shadow-subtle: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
            --shadow-card: 0 10px 15px -3px rgba(0, 0, 0, 0.07), 0 4px 6px -4px rgba(0, 0, 0, 0.05);
            --shadow-hover: 0 20px 25px -5px rgba(0, 60, 165, 0.12), 0 8px 10px -6px rgba(0, 60, 165, 0.08);
            --radius-sm: 6px;
            --radius-md: 10px;
            --radius-lg: 16px;
            --radius-full: 9999px;
            --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            --font-display: 'Bricolage Grotesque', var(--font-sans);
            --font-mono: 'JetBrains Mono', monospace;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-font-smoothing: antialiased;
        }}

        body {{
            background-color: var(--bg-page);
            color: var(--text-dark);
            font-family: var(--font-sans);
            line-height: 1.5;
            overflow-x: hidden;
        }}

        /* === TOP STICKY BAR / REVIEW TOOLBAR === */
        .top-navbar {{
            position: sticky;
            top: 0;
            z-index: 1000;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-light);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
            padding: 12px 24px;
        }}

        .nav-inner {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
        }}

        .nav-brand {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .brand-logo-text {{
            font-family: var(--font-display);
            font-size: 20px;
            font-weight: 800;
            color: var(--primary);
            letter-spacing: -0.5px;
        }}

        .brand-badge-partner {{
            background: #eff6ff;
            color: var(--primary);
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: var(--radius-full);
            border: 1px solid #bfdbfe;
            text-transform: uppercase;
        }}

        .nav-search-wrap {{
            flex: 1;
            max-width: 440px;
            position: relative;
        }}

        .nav-search-input {{
            width: 100%;
            padding: 10px 16px 10px 40px;
            border-radius: var(--radius-full);
            border: 1px solid var(--border-light);
            background: #f8fafc;
            font-size: 14px;
            outline: none;
            transition: all 0.2s;
        }}

        .nav-search-input:focus {{
            border-color: var(--primary);
            background: #fff;
            box-shadow: 0 0 0 3px rgba(0, 60, 165, 0.15);
        }}

        .search-icon {{
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            pointer-events: none;
            font-size: 14px;
        }}

        .nav-actions {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .btn-action {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 9px 16px;
            border-radius: var(--radius-full);
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            border: none;
            transition: all 0.2s;
            text-decoration: none;
        }}

        .btn-pdf {{
            background: linear-gradient(135deg, #003ca5, #002266);
            color: #fff;
            box-shadow: 0 4px 10px rgba(0, 60, 165, 0.25);
        }}

        .btn-pdf:hover {{
            background: linear-gradient(135deg, #004dd4, #003299);
            transform: translateY(-1px);
        }}

        .btn-feedback-panel {{
            background: #fef3c7;
            color: #92400e;
            border: 1px solid #fde68a;
        }}

        .btn-feedback-panel:hover {{
            background: #fde68a;
        }}

        .filter-bar {{
            background: #ffffff;
            border-bottom: 1px solid var(--border-light);
            padding: 10px 24px;
            overflow-x: auto;
            white-space: nowrap;
        }}

        .filter-inner {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            gap: 8px;
            align-items: center;
        }}

        .filter-pill {{
            padding: 6px 14px;
            border-radius: var(--radius-full);
            font-size: 13px;
            font-weight: 600;
            background: #f1f5f9;
            color: var(--text-dark);
            border: 1px solid transparent;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .filter-pill:hover {{
            background: #e2e8f0;
        }}

        .filter-pill.active {{
            background: var(--primary);
            color: #ffffff;
            box-shadow: 0 2px 6px rgba(0, 60, 165, 0.25);
        }}

        .filter-count {{
            background: rgba(255, 255, 255, 0.3);
            padding: 1px 6px;
            border-radius: 10px;
            font-size: 11px;
            margin-left: 4px;
        }}

        /* === EDITORIAL CONTAINER === */
        .catalog-container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px 24px;
        }}

        /* === 1. CAPA (FRONT COVER) === */
        .cover-page {{
            min-height: 92vh;
            background: linear-gradient(145deg, #021638 0%, #002b7f 50%, #0043b8 100%);
            border-radius: var(--radius-lg);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 60px 50px;
            color: #ffffff;
            box-shadow: 0 25px 50px -12px rgba(2, 22, 56, 0.35);
            margin-bottom: 50px;
            page-break-after: always;
            break-after: page;
        }}

        .cover-decor-circle {{
            position: absolute;
            top: -150px;
            right: -150px;
            width: 600px;
            height: 600px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(217, 119, 6, 0.2) 0%, rgba(0, 60, 165, 0) 70%);
            pointer-events: none;
        }}

        .cover-decor-line {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 8px;
            background: linear-gradient(90deg, #d97706, #fbbf24, #003ca5);
        }}

        .cover-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            position: relative;
            z-index: 2;
        }}

        .cover-brand-group {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .cover-brand-title {{
            font-family: var(--font-display);
            font-size: 38px;
            font-weight: 800;
            letter-spacing: -1px;
            color: #ffffff;
            text-transform: uppercase;
        }}

        .cover-brand-sub {{
            font-size: 14px;
            color: #93c5fd;
            letter-spacing: 2px;
            text-transform: uppercase;
            font-weight: 600;
        }}

        .cover-edition-badge {{
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(255, 255, 255, 0.25);
            backdrop-filter: blur(8px);
            padding: 8px 18px;
            border-radius: var(--radius-full);
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 1px;
            color: #fbbf24;
        }}

        .cover-hero-center {{
            position: relative;
            z-index: 2;
            margin: 40px 0;
            max-width: 850px;
        }}

        .cover-tagline {{
            display: inline-block;
            background: rgba(217, 119, 6, 0.25);
            color: #fef3c7;
            border: 1px solid rgba(245, 158, 11, 0.4);
            padding: 6px 14px;
            border-radius: var(--radius-full);
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 20px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}

        .cover-main-heading {{
            font-family: var(--font-display);
            font-size: 58px;
            font-weight: 800;
            line-height: 1.05;
            letter-spacing: -1.5px;
            color: #ffffff;
            margin-bottom: 24px;
        }}

        .cover-main-heading span {{
            color: #fbbf24;
            background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .cover-description {{
            font-size: 18px;
            line-height: 1.6;
            color: #e0e7ff;
            max-width: 680px;
            margin-bottom: 30px;
        }}

        .cover-pillars {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin-top: 30px;
        }}

        .pillar-card {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: var(--radius-md);
            padding: 16px;
            backdrop-filter: blur(6px);
        }}

        .pillar-num {{
            font-family: var(--font-mono);
            font-size: 22px;
            font-weight: 800;
            color: #fbbf24;
            margin-bottom: 4px;
        }}

        .pillar-title {{
            font-size: 13px;
            font-weight: 700;
            color: #ffffff;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .cover-footer {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            border-top: 1px solid rgba(255, 255, 255, 0.15);
            padding-top: 24px;
            position: relative;
            z-index: 2;
            flex-wrap: wrap;
            gap: 16px;
        }}

        .cover-partner-creds {{
            font-size: 14px;
            color: #cbd5e1;
        }}

        .cover-partner-creds strong {{
            color: #ffffff;
            font-size: 15px;
        }}

        .cover-badges-row {{
            display: flex;
            gap: 12px;
        }}

        .cover-badge-item {{
            background: rgba(0, 0, 0, 0.25);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 6px 12px;
            border-radius: var(--radius-sm);
            font-size: 12px;
            color: #e2e8f0;
            font-weight: 600;
        }}

        /* === 2. SUMÁRIO EXECUTIVO & ÍNDICE === */
        .toc-section {{
            background: #ffffff;
            border-radius: var(--radius-lg);
            border: 1px solid var(--border-light);
            padding: 40px;
            margin-bottom: 50px;
            box-shadow: var(--shadow-subtle);
            page-break-after: always;
            break-after: page;
        }}

        .toc-header {{
            text-align: center;
            max-width: 700px;
            margin: 0 auto 36px auto;
        }}

        .toc-header h2 {{
            font-family: var(--font-display);
            font-size: 32px;
            font-weight: 800;
            color: var(--primary);
            margin-bottom: 10px;
        }}

        .toc-header p {{
            color: var(--text-muted);
            font-size: 16px;
        }}

        .toc-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
        }}

        .toc-card {{
            display: flex;
            align-items: center;
            gap: 16px;
            background: #f8fafc;
            border: 1px solid var(--border-light);
            border-radius: var(--radius-md);
            padding: 16px 20px;
            text-decoration: none;
            color: inherit;
            transition: all 0.2s;
        }}

        .toc-card:hover {{
            background: #ffffff;
            border-color: var(--primary);
            box-shadow: var(--shadow-card);
            transform: translateY(-2px);
        }}

        .toc-icon {{
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            flex-shrink: 0;
        }}

        .toc-info {{
            flex: 1;
        }}

        .toc-info h4 {{
            font-size: 15px;
            font-weight: 700;
            color: var(--text-dark);
            margin-bottom: 2px;
        }}

        .toc-info p {{
            font-size: 13px;
            color: var(--text-muted);
        }}

        .toc-arrow {{
            font-weight: 800;
            color: var(--text-light);
            transition: transform 0.2s;
        }}

        .toc-card:hover .toc-arrow {{
            color: var(--primary);
            transform: translateX(4px);
        }}

        /* === 3. SEGMENTOS & CARDS DE PRODUTOS === */
        .segment-section {{
            margin-bottom: 60px;
        }}

        .segment-header {{
            background: #ffffff;
            border-radius: var(--radius-md);
            padding: 24px 30px;
            margin-bottom: 24px;
            box-shadow: var(--shadow-subtle);
            border: 1px solid var(--border-light);
            border-left-width: 6px !important;
        }}

        .seg-title-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }}

        .seg-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            font-weight: 700;
            padding: 4px 12px;
            border-radius: var(--radius-full);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .seg-count {{
            font-family: var(--font-mono);
            font-size: 13px;
            font-weight: 600;
            color: var(--text-muted);
        }}

        .seg-heading {{
            font-family: var(--font-display);
            font-size: 26px;
            font-weight: 800;
            color: var(--text-dark);
            margin-bottom: 6px;
        }}

        .seg-desc {{
            font-size: 14px;
            color: var(--text-muted);
            max-width: 900px;
        }}

        .products-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
            gap: 24px;
        }}

        /* === PRODUTO CARD === */
        .product-card {{
            background: #ffffff;
            border: 1px solid var(--border-light);
            border-radius: var(--radius-lg);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            box-shadow: var(--shadow-subtle);
            page-break-inside: avoid;
            break-inside: avoid;
        }}

        .product-card:hover {{
            transform: translateY(-5px);
            box-shadow: var(--shadow-hover);
            border-color: #cbd5e1;
        }}

        .product-card.card-approved {{
            border-color: #22c55e;
            box-shadow: 0 0 0 2px #86efac;
        }}

        .product-card.card-needs-adjust {{
            border-color: #f59e0b;
            box-shadow: 0 0 0 2px #fde68a;
        }}

        .card-top-bar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 16px 8px 16px;
            background: #ffffff;
            z-index: 2;
        }}

        .card-sku {{
            font-family: var(--font-mono);
            font-size: 12px;
            font-weight: 700;
            color: var(--primary);
            background: #eff6ff;
            padding: 2px 8px;
            border-radius: var(--radius-sm);
        }}

        .card-segment-tag {{
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: var(--radius-full);
            border: 1px solid transparent;
        }}

        .feedback-mark-btn {{
            background: transparent;
            border: none;
            cursor: pointer;
            font-size: 16px;
            padding: 2px;
            border-radius: 50%;
            transition: transform 0.2s;
        }}

        .feedback-mark-btn:hover {{
            transform: scale(1.2);
        }}

        .card-img-container {{
            height: 220px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 16px;
            background: radial-gradient(circle, #ffffff 40%, #f1f5f9 100%);
            position: relative;
            border-bottom: 1px solid #f1f5f9;
        }}

        .card-img {{
            max-height: 100%;
            max-width: 100%;
            object-fit: contain;
            filter: drop-shadow(0 8px 12px rgba(0, 0, 0, 0.08));
            transition: transform 0.3s;
        }}

        .product-card:hover .card-img {{
            transform: scale(1.05);
        }}

        .card-brand-badge {{
            position: absolute;
            bottom: 8px;
            left: 12px;
            background: rgba(15, 23, 42, 0.85);
            color: #ffffff;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            padding: 2px 8px;
            border-radius: var(--radius-sm);
            backdrop-filter: blur(4px);
        }}

        .card-content {{
            padding: 18px;
            display: flex;
            flex-direction: column;
            flex: 1;
            justify-content: space-between;
        }}

        .product-title {{
            font-family: var(--font-display);
            font-size: 16px;
            font-weight: 700;
            color: var(--text-dark);
            margin-bottom: 8px;
            line-height: 1.35;
        }}

        .product-desc {{
            font-size: 12.5px;
            color: var(--text-muted);
            line-height: 1.5;
            margin-bottom: 16px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .spec-section {{
            background: #f8fafc;
            border: 1px solid var(--border-light);
            border-radius: var(--radius-md);
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 16px;
            font-size: 12px;
        }}

        .card-spec-row {{
            display: flex;
            flex-direction: column;
            gap: 3px;
        }}

        .spec-label {{
            font-size: 10.5px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #64748b;
        }}

        .pills-wrap {{
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
        }}

        .spec-pill {{
            font-size: 11px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: var(--radius-sm);
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}

        .pkg-pill {{
            background: #ffffff;
            border: 1px solid #cbd5e1;
            color: #0f172a;
        }}

        .frag-pill {{
            background: #fdf2f8;
            border: 1px solid #fbcfe8;
            color: #9d174d;
        }}

        .pill-icon {{
            font-size: 10px;
        }}

        .active-substance {{
            border-top: 1px dashed var(--border-light);
            padding-top: 6px;
        }}

        .active-val {{
            font-weight: 600;
            color: #0369a1;
            font-size: 11.5px;
            line-height: 1.35;
        }}

        .directions-row {{
            border-top: 1px dashed var(--border-light);
            padding-top: 6px;
        }}

        .directions-val {{
            color: #475569;
            font-size: 11px;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .card-footer {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}

        .btn-site {{
            flex: 1;
            text-align: center;
            padding: 8px 12px;
            background: #eff6ff;
            color: var(--primary);
            border: 1px solid #bfdbfe;
            border-radius: var(--radius-sm);
            font-size: 12px;
            font-weight: 700;
            text-decoration: none;
            transition: all 0.2s;
        }}

        .btn-site:hover {{
            background: var(--primary);
            color: #ffffff;
        }}

        .btn-comment {{
            background: #f1f5f9;
            border: 1px solid var(--border-light);
            color: #475569;
            padding: 8px 12px;
            border-radius: var(--radius-sm);
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
        }}

        .btn-comment:hover {{
            background: #e2e8f0;
            color: #0f172a;
        }}

        /* === 4. CONTRA-CAPA (BACK COVER) === */
        .back-cover-page {{
            min-height: 92vh;
            background: linear-gradient(145deg, #02122c 0%, #001f5c 60%, #002b7f 100%);
            border-radius: var(--radius-lg);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 60px 50px;
            color: #ffffff;
            box-shadow: 0 25px 50px -12px rgba(2, 22, 56, 0.35);
            margin-top: 60px;
            page-break-before: always;
            break-before: page;
        }}

        .back-cover-header {{
            text-align: center;
            max-width: 800px;
            margin: 0 auto;
            position: relative;
            z-index: 2;
        }}

        .back-cover-logo {{
            font-family: var(--font-display);
            font-size: 34px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -1px;
            margin-bottom: 6px;
        }}

        .back-cover-subtitle {{
            font-size: 15px;
            color: #93c5fd;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}

        .back-cover-body {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 30px;
            position: relative;
            z-index: 2;
            margin: 40px 0;
        }}

        .contact-box {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: var(--radius-lg);
            padding: 30px;
            backdrop-filter: blur(10px);
        }}

        .contact-box h3 {{
            font-family: var(--font-display);
            font-size: 20px;
            font-weight: 700;
            color: #fbbf24;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .contact-field {{
            margin-bottom: 14px;
        }}

        .contact-label {{
            font-size: 11px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 3px;
        }}

        .contact-val {{
            font-size: 15px;
            color: #ffffff;
            font-weight: 600;
        }}

        .partner-editable-note {{
            display: inline-block;
            background: rgba(217, 119, 6, 0.2);
            color: #fef3c7;
            border: 1px dashed rgba(245, 158, 11, 0.5);
            font-size: 11px;
            padding: 4px 8px;
            border-radius: 4px;
            margin-top: 10px;
        }}

        .quality-box {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: var(--radius-lg);
            padding: 30px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .quality-box h3 {{
            font-family: var(--font-display);
            font-size: 20px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 14px;
        }}

        .quality-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 12px;
            font-size: 13.5px;
            color: #cbd5e1;
        }}

        .quality-list li {{
            display: flex;
            align-items: flex-start;
            gap: 10px;
        }}

        .quality-list li::before {{
            content: "✓";
            color: #fbbf24;
            font-weight: 800;
        }}

        .back-cover-footer {{
            border-top: 1px solid rgba(255, 255, 255, 0.15);
            padding-top: 24px;
            text-align: center;
            font-size: 12px;
            color: #94a3b8;
            position: relative;
            z-index: 2;
        }}

        /* === MODAL DE PALPITES / FEEDBACK === */
        .modal-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(4px);
            z-index: 2000;
            display: none;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}

        .modal-box {{
            background: #ffffff;
            border-radius: var(--radius-lg);
            width: 100%;
            max-width: 520px;
            padding: 24px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            position: relative;
            animation: modalPop 0.2s ease-out;
        }}

        @keyframes modalPop {{
            from {{ transform: scale(0.95); opacity: 0; }}
            to {{ transform: scale(1); opacity: 1; }}
        }}

        .modal-title {{
            font-family: var(--font-display);
            font-size: 18px;
            font-weight: 700;
            color: var(--text-dark);
            margin-bottom: 4px;
        }}

        .modal-subtitle {{
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 16px;
        }}

        .modal-textarea {{
            width: 100%;
            height: 120px;
            border: 1px solid var(--border-light);
            border-radius: var(--radius-md);
            padding: 12px;
            font-family: var(--font-sans);
            font-size: 14px;
            outline: none;
            resize: vertical;
            margin-bottom: 16px;
        }}

        .modal-textarea:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(0, 60, 165, 0.15);
        }}

        .modal-status-select {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }}

        .status-radio-label {{
            flex: 1;
            padding: 8px 12px;
            border: 1px solid var(--border-light);
            border-radius: var(--radius-md);
            font-size: 13px;
            font-weight: 600;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .status-radio-label input {{
            display: none;
        }}

        .status-radio-label:has(input:checked) {{
            border-color: var(--primary);
            background: #eff6ff;
            color: var(--primary);
        }}

        .modal-actions {{
            display: flex;
            justify-content: flex-end;
            gap: 10px;
        }}

        /* === PAINEL LATERAL DE PALPITES (DRAWER) === */
        .drawer-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.4);
            z-index: 1500;
            display: none;
        }}

        .feedback-drawer {{
            position: fixed;
            top: 0;
            right: 0;
            width: 440px;
            max-width: 90vw;
            height: 100vh;
            background: #ffffff;
            box-shadow: -10px 0 30px rgba(0, 0, 0, 0.15);
            z-index: 1600;
            transform: translateX(100%);
            transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex;
            flex-direction: column;
        }}

        .feedback-drawer.open {{
            transform: translateX(0);
        }}

        .drawer-header {{
            padding: 20px;
            border-bottom: 1px solid var(--border-light);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .drawer-header h3 {{
            font-family: var(--font-display);
            font-size: 18px;
            font-weight: 800;
            color: var(--primary);
        }}

        .drawer-close-btn {{
            background: transparent;
            border: none;
            font-size: 20px;
            cursor: pointer;
            color: var(--text-muted);
        }}

        .drawer-body {{
            padding: 20px;
            overflow-y: auto;
            flex: 1;
        }}

        .drawer-footer {{
            padding: 16px 20px;
            border-top: 1px solid var(--border-light);
            display: flex;
            gap: 10px;
        }}

        /* === PRINT & PDF STYLES === */
        @media print {{
            @page {{
                size: A4 portrait;
                margin: 10mm;
            }}

            body {{
                background: #ffffff !important;
                color: #000000 !important;
                font-size: 11pt;
            }}

            .top-navbar,
            .filter-bar,
            .btn-comment,
            .feedback-mark-btn,
            .modal-overlay,
            .drawer-overlay,
            .feedback-drawer,
            .btn-site {{
                display: none !important;
            }}

            .catalog-container {{
                max-width: 100% !important;
                padding: 0 !important;
                margin: 0 !important;
            }}

            .cover-page {{
                min-height: 280mm !important;
                border-radius: 0 !important;
                box-shadow: none !important;
                page-break-after: always !important;
                break-after: page !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }}

            .toc-section {{
                border-radius: 0 !important;
                box-shadow: none !important;
                border: 1px solid #ccc !important;
                page-break-after: always !important;
                break-after: page !important;
            }}

            .segment-section {{
                page-break-before: always !important;
                break-before: page !important;
            }}

            .products-grid {{
                grid-template-columns: repeat(2, 1fr) !important;
                gap: 14mm !important;
            }}

            .product-card {{
                box-shadow: none !important;
                border: 1px solid #cbd5e1 !important;
                break-inside: avoid !important;
                page-break-inside: avoid !important;
            }}

            .back-cover-page {{
                min-height: 280mm !important;
                border-radius: 0 !important;
                box-shadow: none !important;
                page-break-before: always !important;
                break-before: page !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }}

            * {{
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }}
        }}

        /* === RESPONSIVE TWEAKS === */
        @media (max-width: 768px) {{
            .cover-main-heading {{
                font-size: 36px;
            }}
            .cover-page, .back-cover-page {{
                padding: 30px 20px;
            }}
            .products-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>

    <!-- TOP NAVBAR & PALPITES CONTROLS -->
    <header class="top-navbar">
        <div class="nav-inner">
            <div class="nav-brand">
                <span class="brand-logo-text">START QUÍMICA</span>
                <span class="brand-badge-partner">Parceiro Autorizado</span>
            </div>

            <div class="nav-search-wrap">
                <span class="search-icon">🔍</span>
                <input type="text" id="liveSearch" class="nav-search-input" placeholder="Buscar por produto, fragrância, ativo ou embalagem..." oninput="handleSearch()">
            </div>

            <div class="nav-actions">
                <button class="btn-action btn-pdf" onclick="window.print()">
                    <span>🖨️</span> Salvar / Imprimir em PDF (A4)
                </button>
                <button class="btn-action btn-feedback-panel" onclick="toggleDrawer()">
                    <span>💬</span> Palpites & Aprovação (<span id="feedbackCounter">0</span>)
                </button>
            </div>
        </div>
    </header>

    <!-- FILTER BAR -->
    <div class="filter-bar">
        <div class="filter-inner">
            <button class="filter-pill active" onclick="filterSegment('all', this)">
                Todos os Produtos <span class="filter-count">80</span>
            </button>
            <button class="filter-pill" onclick="filterSegment('Lavanderia e Tratamento de Roupas', this)">
                🧺 Lavanderia <span class="filter-count">{len(by_segment.get('Lavanderia e Tratamento de Roupas', []))}</span>
            </button>
            <button class="filter-pill" onclick="filterSegment('Pisos, Pedras e Tratamento de Superfícies', this)">
                🏛️ Pisos & Pedras <span class="filter-count">{len(by_segment.get('Pisos, Pedras e Tratamento de Superfícies', []))}</span>
            </button>
            <button class="filter-pill" onclick="filterSegment('Desinfecção e Limpeza Geral Multiuso', this)">
                ✨ Desinfecção & Limpeza <span class="filter-count">{len(by_segment.get('Desinfecção e Limpeza Geral Multiuso', []))}</span>
            </button>
            <button class="filter-pill" onclick="filterSegment('Cozinha e Tratamento de Metais', this)">
                🍳 Cozinha & Metais <span class="filter-count">{len(by_segment.get('Cozinha e Tratamento de Metais', []))}</span>
            </button>
            <button class="filter-pill" onclick="filterSegment('Higiene Pessoal e Antissepsia', this)">
                🧴 Asseptgel & Higiene <span class="filter-count">{len(by_segment.get('Higiene Pessoal e Antissepsia', []))}</span>
            </button>
            <button class="filter-pill" onclick="filterSegment('Aromatização e Cuidados Pet', this)">
                🌸 Aromatizantes & Pet <span class="filter-count">{len(by_segment.get('Aromatização e Cuidados Pet', []))}</span>
            </button>
            <button class="filter-pill" onclick="filterSegment('Automotivo e Oficinas', this)">
                🚗 Linha Automotiva <span class="filter-count">{len(by_segment.get('Automotivo e Oficinas', []))}</span>
            </button>
        </div>
    </div>

    <main class="catalog-container">

        <!-- 1. CAPA DO CATÁLOGO (FRONT COVER) -->
        <div class="cover-page">
            <div class="cover-decor-circle"></div>
            <div class="cover-decor-line"></div>

            <div class="cover-header">
                <div class="cover-brand-group">
                    <div class="cover-brand-title">Start Química</div>
                    <div class="cover-brand-sub">Soluções Químicas Profissionais e Domésticas</div>
                </div>
                <div class="cover-edition-badge">
                    EDIÇÃO 2026 / 2027
                </div>
            </div>

            <div class="cover-hero-center">
                <div class="cover-tagline">Portfólio de Alta Performance</div>
                <h1 class="cover-main-heading">
                    Catálogo Oficial de <span>Produtos e Soluções</span>
                </h1>
                <p class="cover-description">
                    Apresentação completa das linhas de saneantes, desengordurantes, desinfetantes, ceras nobres, tratamento de tecidos, antissepsia pessoal e cuidados automotivos com respaldo técnico e qualidade de fabricação Start Química.
                </p>

                <div class="cover-pillars">
                    <div class="pillar-card">
                        <div class="pillar-num">80+</div>
                        <div class="pillar-title">Produtos Homologados</div>
                    </div>
                    <div class="pillar-card">
                        <div class="pillar-num">7</div>
                        <div class="pillar-title">Segmentos de Aplicação</div>
                    </div>
                    <div class="pillar-card">
                        <div class="pillar-num">100%</div>
                        <div class="pillar-title">Fórmulas Certificadas Anvisa</div>
                    </div>
                    <div class="pillar-card">
                        <div class="pillar-num">PIM</div>
                        <div class="pillar-title">Imagens Oficiais de Estúdio</div>
                    </div>
                </div>
            </div>

            <div class="cover-footer">
                <div class="cover-partner-creds">
                    Apresentado por: <strong>Distribuidor & Parceiro Comercial Autorizado</strong><br>
                    Linhas: Azulim &bull; Tuff &bull; Pedrex &bull; Asseptgel &bull; Indy Cryl &bull; Only &bull; Maximoom
                </div>
                <div class="cover-badges-row">
                    <span class="cover-badge-item">Registro Anvisa</span>
                    <span class="cover-badge-item">Tensoativos Biodegradáveis</span>
                    <span class="cover-badge-item">Rigor Técnico</span>
                </div>
            </div>
        </div>

        <!-- 2. APRESENTAÇÃO & ÍNDICE DE SEGMENTOS (SUMÁRIO) -->
        <section class="toc-section">
            <div class="toc-header">
                <h2>Índice Geral de Segmentos</h2>
                <p>Navegue pelos segmentos especializados de produtos desenvolvidos para atender as mais exigentes rotinas de higienização, manutenção e acabamento.</p>
            </div>
            <div class="toc-grid">
                {''.join(toc_items)}
            </div>
        </section>

        <!-- 3. MIOLO COM OS SEGMENTOS E PRODUTOS -->
        {''.join(segments_html)}

        <!-- 4. CONTRA-CAPA (BACK COVER) -->
        <div class="back-cover-page">
            <div class="cover-decor-line"></div>

            <div class="back-cover-header">
                <div class="back-cover-logo">START QUÍMICA</div>
                <div class="back-cover-subtitle">Inovação, Eficiência e Confiança em Cada Solução</div>
            </div>

            <div class="back-cover-body">
                <div class="contact-box">
                    <h3>🤝 Atendimento & Distribuição</h3>
                    
                    <div class="contact-field">
                        <div class="contact-label">Parceiro / Distribuidor:</div>
                        <div class="contact-val">Distribuição Autorizada Start Química</div>
                    </div>

                    <div class="contact-field">
                        <div class="contact-label">Contato Comercial / Pedidos:</div>
                        <div class="contact-val">(DDD) 00000-0000 / WhatsApp</div>
                    </div>

                    <div class="contact-field">
                        <div class="contact-label">E-mail:</div>
                        <div class="contact-val">contato@parceirostart.com.br</div>
                    </div>

                    <div class="contact-field">
                        <div class="contact-label">Região de Atendimento:</div>
                        <div class="contact-val">Atendimento Regional & Entregas Programadas</div>
                    </div>

                    <div class="partner-editable-note">
                        💡 Este bloco de contato pode ser personalizado com seus dados comerciais completos no arquivo final.
                    </div>
                </div>

                <div class="quality-box">
                    <h3>Padrões Técnicos e Compromisso</h3>
                    <ul class="quality-list">
                        <li>Fórmulas desenvolvidas sob rigoroso controle de qualidade em laboratório homologado.</li>
                        <li>Tensoativos e ativos biodegradáveis com alto compromisso ambiental.</li>
                        <li>Economia comprovada com altas taxas de diluição para uso comercial e industrial.</li>
                        <li>Assistência técnica e orientações para treinamento de equipes de limpeza.</li>
                        <li>Notificações e registros vigentes junto à ANVISA / Ministério da Saúde.</li>
                    </ul>
                </div>
            </div>

            <div class="back-cover-footer">
                <p>&copy; 2026 Start Química. Todos os direitos reservados. Marcas e imagens de propriedade de Start Química Indústria e Comércio Ltda.<br>
                Catálogo técnico organizado para uso comercial de parceiros e clientes autorizados.</p>
            </div>
        </div>

    </main>

    <!-- MODAL DE PALPITE / COMENTÁRIO INDIVIDUAL -->
    <div class="modal-overlay" id="commentModal" onclick="closeCommentModal(event)">
        <div class="modal-box" onclick="event.stopPropagation()">
            <h3 class="modal-title" id="modalProductTitle">Deixar Palpite sobre o Produto</h3>
            <p class="modal-subtitle" id="modalProductSubtitle">Adicione sugestões de alteração no texto, foto ou especificações:</p>
            
            <div class="modal-status-select">
                <label class="status-radio-label">
                    <input type="radio" name="prodStatus" value="approved">
                    ✅ Aprovado
                </label>
                <label class="status-radio-label">
                    <input type="radio" name="prodStatus" value="adjust" checked>
                    ⚠️ Sugerir Ajuste
                </label>
                <label class="status-radio-label">
                    <input type="radio" name="prodStatus" value="neutral">
                    ⚪ Neutro
                </label>
            </div>

            <textarea id="modalCommentText" class="modal-textarea" placeholder="Ex: Mudar o volume principal, adicionar foto da embalagem de 5L, alterar indicação de uso..."></textarea>
            
            <div class="modal-actions">
                <button class="btn-action" style="background:#e2e8f0; color:#334155;" onclick="closeCommentModal()">Cancelar</button>
                <button class="btn-action btn-pdf" onclick="saveProductComment()">Salvar Palpite</button>
            </div>
        </div>
    </div>

    <!-- DRAWER LATERAL DE FEEDBACKS / RESUMO DE PALPITES -->
    <div class="drawer-overlay" id="drawerOverlay" onclick="toggleDrawer()"></div>
    <div class="feedback-drawer" id="feedbackDrawer">
        <div class="drawer-header">
            <h3>📝 Painel de Palpites & Feedback</h3>
            <button class="drawer-close-btn" onclick="toggleDrawer()">&times;</button>
        </div>
        <div class="drawer-body" id="drawerList">
            <p style="color: #64748b; font-size: 14px;">Nenhum palpite registrado ainda. Clique no botão "💬 Palpite / Ajuste" em qualquer produto ou marque as bolinhas para aprovar/ajustar.</p>
        </div>
        <div class="drawer-footer">
            <button class="btn-action btn-pdf" style="flex:1;" onclick="copyFeedbackToClipboard()">📋 Copiar Resumo dos Palpites</button>
            <button class="btn-action" style="background:#f1f5f9; color:#475569;" onclick="clearAllFeedbacks()">Limpar</button>
        </div>
    </div>

    <script>
        // Store feedbacks in memory & localStorage
        let feedbackData = JSON.parse(localStorage.getItem('start_catalog_feedbacks') || '{{}}');
        let currentModalProductId = null;

        function updateFeedbackUI() {{
            const keys = Object.keys(feedbackData);
            document.getElementById('feedbackCounter').innerText = keys.length;

            // Reset all card styles
            document.querySelectorAll('.product-card').forEach(card => {{
                card.classList.remove('card-approved', 'card-needs-adjust');
                const btn = card.querySelector('.feedback-mark-btn');
                if (btn) btn.innerText = '⚪';
            }});

            const drawerList = document.getElementById('drawerList');
            if (keys.length === 0) {{
                drawerList.innerHTML = '<p style="color: #64748b; font-size: 14px; text-align:center; padding: 30px 10px;">Nenhum palpite ou anotação registrada ainda.<br><br>💡 Você ou a pessoa que está revisando podem clicar em <strong>"💬 Palpite / Ajuste"</strong> nos produtos para sugerir mudanças de texto, foto ou embalagem.</p>';
                return;
            }}

            let listHtml = '';
            keys.forEach(id => {{
                const item = feedbackData[id];
                const card = document.querySelector(`.product-card[data-id="${{id}}"]`);
                if (card) {{
                    const btn = card.querySelector('.feedback-mark-btn');
                    if (item.status === 'approved') {{
                        card.classList.add('card-approved');
                        if (btn) btn.innerText = '✅';
                    }} else if (item.status === 'adjust') {{
                        card.classList.add('card-needs-adjust');
                        if (btn) btn.innerText = '⚠️';
                    }}
                }}

                const badge = item.status === 'approved' ? '<span style="color:#16a34a; font-weight:700;">✅ Aprovado</span>' : '<span style="color:#d97706; font-weight:700;">⚠️ Ajuste</span>';
                listHtml += `
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px; margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <strong style="font-size:13px; color:#0f172a;">#${{String(id).padStart(3, '0')}} - ${{item.name}}</strong>
                            ${{badge}}
                        </div>
                        <p style="font-size:13px; color:#334155; line-height:1.4;">${{item.comment ? item.comment : '<em>Sem observação de texto</em>'}}</p>
                        <div style="text-align:right; margin-top:8px;">
                            <button onclick="removeFeedback(${{id}})" style="background:none; border:none; color:#ef4444; font-size:11px; cursor:pointer;">Remover</button>
                        </div>
                    </div>
                `;
            }});
            drawerList.innerHTML = listHtml;
            localStorage.setItem('start_catalog_feedbacks', JSON.stringify(feedbackData));
        }}

        function toggleApproval(id) {{
            const card = document.querySelector(`.product-card[data-id="${{id}}"]`);
            const title = card.querySelector('.product-title').innerText;
            if (!feedbackData[id]) {{
                feedbackData[id] = {{ name: title, status: 'approved', comment: '' }};
            }} else if (feedbackData[id].status === 'approved') {{
                feedbackData[id].status = 'adjust';
            }} else {{
                delete feedbackData[id];
            }}
            updateFeedbackUI();
        }}

        function openCommentModal(id) {{
            currentModalProductId = id;
            const card = document.querySelector(`.product-card[data-id="${{id}}"]`);
            const title = card.querySelector('.product-title').innerText;
            document.getElementById('modalProductTitle').innerText = '#' + String(id).padStart(3, '0') + ' - ' + title;
            
            const existing = feedbackData[id];
            if (existing) {{
                document.getElementById('modalCommentText').value = existing.comment || '';
                const rad = document.querySelector(`input[name="prodStatus"][value="${{existing.status}}"]`);
                if (rad) rad.checked = true;
            }} else {{
                document.getElementById('modalCommentText').value = '';
                document.querySelector('input[name="prodStatus"][value="adjust"]').checked = true;
            }}
            document.getElementById('commentModal').style.display = 'flex';
        }}

        function closeCommentModal(e) {{
            if (e && e.target !== document.getElementById('commentModal')) return;
            document.getElementById('commentModal').style.display = 'none';
        }}

        function saveProductComment() {{
            if (!currentModalProductId) return;
            const card = document.querySelector(`.product-card[data-id="${{currentModalProductId}}"]`);
            const title = card.querySelector('.product-title').innerText;
            const comment = document.getElementById('modalCommentText').value.trim();
            const status = document.querySelector('input[name="prodStatus"]:checked').value;
            
            feedbackData[currentModalProductId] = {{
                name: title,
                status: status,
                comment: comment
            }};
            document.getElementById('commentModal').style.display = 'none';
            updateFeedbackUI();
        }}

        function removeFeedback(id) {{
            delete feedbackData[id];
            updateFeedbackUI();
        }}

        function clearAllFeedbacks() {{
            if (confirm('Deseja limpar todos os palpites registrados?')) {{
                feedbackData = {{}};
                updateFeedbackUI();
            }}
        }}

        function toggleDrawer() {{
            const drawer = document.getElementById('feedbackDrawer');
            const overlay = document.getElementById('drawerOverlay');
            if (drawer.classList.contains('open')) {{
                drawer.classList.remove('open');
                overlay.style.display = 'none';
            }} else {{
                drawer.classList.add('open');
                overlay.style.display = 'block';
            }}
        }}

        function copyFeedbackToClipboard() {{
            const keys = Object.keys(feedbackData);
            if (keys.length === 0) {{
                alert('Nenhum palpite para copiar.');
                return;
            }}
            let text = '=== PALPITES & FEEDBACK DO CATÁLOGO START QUÍMICA ===\\n\\n';
            keys.forEach(id => {{
                const item = feedbackData[id];
                const statusStr = item.status === 'approved' ? '[APROVADO]' : '[AJUSTE SUGERIDO]';
                text += `#${{String(id).padStart(3, '0')}} - ${{item.name}}\\nStatus: ${{statusStr}}\\n`;
                if (item.comment) text += `Observação: ${{item.comment}}\\n`;
                text += '-------------------------------------\\n';
            }});
            navigator.clipboard.writeText(text).then(() => {{
                alert('Resumo dos palpites copiado para a área de transferência! Você pode colar no WhatsApp ou enviar por e-mail.');
            }});
        }}

        // Live Search Filter
        function handleSearch() {{
            const q = document.getElementById('liveSearch').value.toLowerCase().trim();
            const cards = document.querySelectorAll('.product-card');
            cards.forEach(card => {{
                const name = card.getAttribute('data-name');
                const active = card.getAttribute('data-active');
                const frag = card.getAttribute('data-fragrance');
                const text = card.innerText.toLowerCase();
                if (!q || name.includes(q) || active.includes(q) || frag.includes(q) || text.includes(q)) {{
                    card.style.display = 'flex';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}

        // Segment Filter
        function filterSegment(seg, btn) {{
            document.querySelectorAll('.filter-pill').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const sections = document.querySelectorAll('.segment-section');
            if (seg === 'all') {{
                sections.forEach(s => s.style.display = 'block');
            }} else {{
                sections.forEach(s => {{
                    const header = s.querySelector('.seg-heading').innerText;
                    if (header.includes(seg) || seg.includes(header)) {{
                        s.style.display = 'block';
                    }} else {{
                        s.style.display = 'none';
                    }}
                }});
            }}
        }}

        // Initialize UI
        document.addEventListener('DOMContentLoaded', () => {{
            updateFeedbackUI();
        }});
        updateFeedbackUI();
    </script>
</body>
</html>
"""

with open('catalogo_visual.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print("Catálogo completo e elegante gerado com sucesso em catalogo_visual.html!")

