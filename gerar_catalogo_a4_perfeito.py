import json
import os
import re
import urllib.parse

with open('catalogo_detalhado.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

# Segment styles tailored to Dona Lu's visual universe
SEGMENT_STYLES = {
    "Pisos, Pedras e Tratamento de Superfícies": {
        "icon": "🏛️",
        "bg": "#fef9c3",
        "text": "#854d0e",
        "border": "#fde047",
        "color": "#ca8a04",
        "badge_bg": "#fffbeb",
        "short": "Pisos & Pedras",
        "desc": "Soluções profissionais para pós-obra, restauração, proteção e acabamento de pedras rústicas, cerâmicas, porcelanatos e pisos vinílicos."
    },
    "Desinfecção e Limpeza Geral Multiuso": {
        "icon": "✨",
        "bg": "#e0f2fe",
        "text": "#075985",
        "border": "#bae6fd",
        "color": "#0284c7",
        "badge_bg": "#f0f9ff",
        "short": "Limpeza Geral",
        "desc": "Alto poder bactericida e ação desengordurante profunda para manutenção diária e pesada em empresas, condomínios e indústrias."
    },
    "Lavanderia e Tratamento de Roupas": {
        "icon": "🧺",
        "bg": "#ede9fe",
        "text": "#5b21b6",
        "border": "#ddd6fe",
        "color": "#7c3aed",
        "badge_bg": "#f5f3ff",
        "short": "Lavanderia",
        "desc": "Fórmulas de alta tecnologia com enzimas ativas, oxigênio puro e microcápsulas de perfume para hotelaria, lavanderias e uso doméstico."
    },
    "Cozinha e Tratamento de Metais": {
        "icon": "🍳",
        "bg": "#ffedd5",
        "text": "#9a3412",
        "border": "#fed7aa",
        "color": "#ea580c",
        "badge_bg": "#fff7ed",
        "short": "Cozinha & Metais",
        "desc": "Remoção instantânea de crostas e gorduras pesadas, desengordurantes industriais, polimento de inox e restauração de alumínio."
    },
    "Higiene Pessoal e Antissepsia": {
        "icon": "🧴",
        "bg": "#dcfce7",
        "text": "#166534",
        "border": "#bbf7d0",
        "color": "#16a34a",
        "badge_bg": "#f0fdf4",
        "short": "Higiene & Asseptgel",
        "desc": "Linha Asseptgel com eficácia comprovada contra germes e bactérias, álcool 70º hidratante e sabonetes antissépticos."
    },
    "Automotivo e Oficinas": {
        "icon": "🚗",
        "bg": "#f1f5f9",
        "text": "#1e293b",
        "border": "#cbd5e1",
        "color": "#475569",
        "badge_bg": "#f8fafc",
        "short": "Linha Automotiva",
        "desc": "Estética automotiva profissional: revitalização de pneus, silicones puros, hidratação de couros e ceras de alto brilho."
    },
    "Aromatização e Cuidados Pet": {
        "icon": "🌸",
        "bg": "#fae8ff",
        "text": "#86198f",
        "border": "#f5d0fe",
        "color": "#c026d3",
        "badge_bg": "#fdf4ff",
        "short": "Aromatizantes & Pet",
        "desc": "Fragrâncias finas e neutralizadores biológicos de odores para ambientes corporativos, condomínios e lares com animais de estimação."
    }
}

# Thematic order of segments
segment_order = [
    "Pisos, Pedras e Tratamento de Superfícies",
    "Desinfecção e Limpeza Geral Multiuso",
    "Lavanderia e Tratamento de Roupas",
    "Cozinha e Tratamento de Metais",
    "Higiene Pessoal e Antissepsia",
    "Aromatização e Cuidados Pet",
    "Automotivo e Oficinas"
]

products_sorted = sorted(products, key=lambda p: (
    segment_order.index(p['segment']) if p['segment'] in segment_order else 99,
    p['index']
))

# Group products into exact 4-item pages
product_pages = []
for i in range(0, len(products_sorted), 4):
    product_pages.append(products_sorted[i:i+4])

def render_compact_card(p):
    safe_png = f"imagens_produtos/{p['png_file'].replace('%', '%25')}"
    seg_info = SEGMENT_STYLES.get(p['segment'], {
        "icon": "📦", "bg": "#f8fafc", "text": "#334155", "border": "#e2e8f0", "color": "#003CA5", "badge_bg": "#fff", "short": "Geral"
    })
    
    # Packaging
    pkg_list = [x.strip() for x in p['packaging'].split(',') if x.strip()]
    pkg_str = " · ".join(pkg_list[:4])
    
    # Fragrance
    frag_list = [x.strip() for x in p['fragrance'].split(',') if x.strip()]
    frag_str = ", ".join(frag_list[:3])
    
    # WhatsApp request link
    wa_msg = urllib.parse.quote(f"Olá Dona Lu! Tenho interesse no produto: {p['name']} (Item #{p['index']:03d}). Poderia me passar um orçamento/informações?")
    
    return f"""
    <div class="a4-product-card" 
         data-id="{p['index']}" 
         data-segment="{p['segment']}" 
         data-name="{p['name'].lower()}" 
         data-active="{p['active'].lower()}" 
         data-fragrance="{p['fragrance'].lower()}"
         data-brand="{p['brand'].lower()}">
        
        <div class="card-head">
            <div class="sku-badge">#{p['index']:03d}</div>
            <div class="card-seg-pill" style="background:{seg_info['badge_bg']}; color:{seg_info['text']}; border: 1px solid {seg_info['border']};">
                {seg_info['icon']} {seg_info['short']}
            </div>
            <button class="feedback-mark-btn" onclick="toggleApproval({p['index']})" title="Marcar status / Feedback" id="btn-status-{p['index']}">
                ⚪
            </button>
        </div>

        <div class="card-visual">
            <div class="packshot-glow"></div>
            <img src="{safe_png}" alt="{p['name']}" loading="lazy" class="packshot-img" onerror="this.onerror=null; this.src='{safe_png.replace('%25', '%')}';">
            <span class="brand-tag">{p['brand']}</span>
        </div>

        <div class="card-details">
            <h4 class="card-product-name">{p['name']}</h4>
            
            <div class="specs-mini-table">
                <div class="spec-mini-row">
                    <span class="spec-k">Embalagens:</span>
                    <span class="spec-v bold-pkg">{pkg_str}</span>
                </div>
                <div class="spec-mini-row">
                    <span class="spec-k">Fragrância:</span>
                    <span class="spec-v">{frag_str}</span>
                </div>
                <div class="spec-mini-row active-mini-row">
                    <span class="spec-k-active">Ativo:</span>
                    <span class="spec-v-active">{p['active']}</span>
                </div>
                <div class="spec-mini-row directions-mini-row">
                    <span class="spec-k">Aplicação:</span>
                    <span class="spec-v directions-clamp">{p['directions']}</span>
                </div>
            </div>

            <div class="card-btns">
                <a href="https://wa.me/5517981321919?text={wa_msg}" target="_blank" class="btn-card-wa" title="Pedir no WhatsApp">
                    <span>Pedir no WhatsApp</span>
                </a>
                <a href="{p['product_url']}" target="_blank" class="btn-card-site" title="Ver no site Start Química">
                    Ficha Técnica
                </a>
                <button class="btn-card-feedback" onclick="openCommentModal({p['index']})" title="Deixar palpite">
                    💬 Palpite
                </button>
            </div>
        </div>
    </div>
    """

# Build each A4 product sheet
rendered_product_sheets = []
total_pages = len(product_pages)

for page_idx, page_items in enumerate(product_pages, start=1):
    # Find predominant segment on this page
    page_segs = list(dict.fromkeys([p['segment'] for p in page_items]))
    main_seg = page_segs[0]
    seg_info = SEGMENT_STYLES.get(main_seg, SEGMENT_STYLES["Desinfecção e Limpeza Geral Multiuso"])
    
    cards_html = "\n".join([render_compact_card(p) for p in page_items])
    
    sheet_html = f"""
    <div class="a4-sheet" data-page-num="{page_idx}">
        <!-- RUNNING HEADER -->
        <header class="sheet-header">
            <div class="sheet-header-left">
                <img src="assets_donalu/logo-donalu-128.png" alt="Dona Lu" class="sheet-logo-mini">
                <div class="sheet-header-brand">
                    <span class="sheet-brand-name">DONA LU · PRODUTOS DE LIMPEZA</span>
                    <span class="sheet-brand-sub">Distribuidora Autorizada Start Química · São José do Rio Preto</span>
                </div>
            </div>
            <div class="sheet-header-right">
                <span class="sheet-seg-pill" style="background:{seg_info['badge_bg']}; color:{seg_info['text']}; border: 1px solid {seg_info['border']};">
                    {seg_info['icon']} {seg_info['short']}
                </span>
            </div>
        </header>

        <!-- 2x2 PRODUCT GRID (EXACTLY 4 PRODUCTS) -->
        <div class="sheet-grid-2x2">
            {cards_html}
        </div>

        <!-- RUNNING FOOTER -->
        <footer class="sheet-footer">
            <div class="sheet-footer-left">
                <span>Central de Pedidos: <strong>(17) 98132-1919 (WhatsApp)</strong> · donalumateriais@gmail.com</span>
            </div>
            <div class="sheet-footer-right">
                <span class="sheet-page-counter">Página <strong>{page_idx:02d}</strong> de {total_pages:02d}</span>
            </div>
        </footer>
    </div>
    """
    rendered_product_sheets.append(sheet_html)

# Build Table of Contents cards
toc_items = []
current_page_counter = 1
for seg_name in segment_order:
    seg_info = SEGMENT_STYLES[seg_name]
    seg_products = [p for p in products_sorted if p['segment'] == seg_name]
    if not seg_products:
        continue
    # find first page this segment appears
    first_page = 1
    for p_idx, p_list in enumerate(product_pages, start=1):
        if any(p['segment'] == seg_name for p in p_list):
            first_page = p_idx
            break
            
    toc_items.append(f"""
        <div class="toc-row-card">
            <div class="toc-icon-circle" style="background:{seg_info['bg']}; color:{seg_info['text']}; border: 1px solid {seg_info['border']};">
                {seg_info['icon']}
            </div>
            <div class="toc-row-details">
                <h4 class="toc-row-title">{seg_name}</h4>
                <p class="toc-row-desc">{seg_info['desc']}</p>
            </div>
            <div class="toc-row-meta">
                <span class="toc-count-pill">{len(seg_products)} produtos</span>
                <span class="toc-page-num">Pág. {first_page:02d}</span>
            </div>
        </div>
    """)

# Assemble Full Master Document
full_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo Oficial Dona Lu — Produtos de Limpeza Profissional (Edição A4 / PDF)</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=Montserrat:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
    <link rel="icon" type="image/png" href="assets_donalu/logo-donalu-128.png">
    
    <style>
        /* === DONA LU BRAND TOKENS & FIGMA / CANVA SPECS === */
        :root {{
            --donalu-navy:          #001F56;
            --donalu-navy-dark:     #001438;
            --donalu-navy-2:        #162239;
            --donalu-blue-primary:  #003CA5;
            --donalu-blue-dark:     #002E80;
            --donalu-blue-light:    #E6EEFA;
            --donalu-yellow:        #FDB827;
            --donalu-yellow-dark:   #E9A30F;
            --donalu-yellow-light:  #FFF4D6;
            --donalu-whatsapp:      #25D366;
            --donalu-whatsapp-dark: #1EBE5D;
            --donalu-bg:            #525659; /* PDF viewer gray background */
            --donalu-sheet-bg:      #FFFFFF;
            --donalu-text:          #162239;
            --donalu-text-muted:    #5A6A88;
            --donalu-border:        #E2E8F0;
            
            --font-display: 'Bricolage Grotesque', 'Montserrat', sans-serif;
            --font-body:    'Montserrat', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            --font-mono:    'JetBrains Mono', monospace;
            
            --radius-sm: 5px;
            --radius-md: 10px;
            --radius-lg: 16px;
            --radius-pill: 9999px;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-font-smoothing: antialiased;
        }}

        body {{
            background-color: var(--donalu-bg);
            color: var(--donalu-text);
            font-family: var(--font-body);
            line-height: 1.45;
            padding-bottom: 60px;
        }}

        /* === TOPBAR & REVIEW CONTROLS (SCREEN ONLY) === */
        .donalu-topbar {{
            position: sticky;
            top: 0;
            z-index: 1000;
            background: rgba(0, 31, 86, 0.98);
            backdrop-filter: blur(12px);
            border-bottom: 3px solid var(--donalu-yellow);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.35);
            padding: 10px 24px;
            color: #ffffff;
        }}

        .topbar-inner {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
        }}

        .topbar-brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
            color: inherit;
        }}

        .topbar-logo {{
            height: 42px;
            width: 42px;
            object-fit: contain;
            background: #ffffff;
            border-radius: 50%;
            padding: 2px;
            box-shadow: 0 0 0 2px var(--donalu-yellow);
        }}

        .topbar-brand-title {{
            font-family: var(--font-display);
            font-size: 19px;
            font-weight: 800;
            color: #ffffff;
        }}

        .topbar-brand-title span {{
            color: var(--donalu-yellow);
        }}

        .topbar-brand-subtitle {{
            font-size: 11px;
            font-weight: 600;
            color: #b8c4dc;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .topbar-search {{
            flex: 1;
            max-width: 400px;
            position: relative;
        }}

        .topbar-search input {{
            width: 100%;
            padding: 9px 16px 9px 38px;
            border-radius: var(--radius-pill);
            border: 1px solid rgba(255, 255, 255, 0.25);
            background: rgba(255, 255, 255, 0.12);
            color: #ffffff;
            font-family: var(--font-body);
            font-size: 13px;
            outline: none;
            transition: all 0.2s;
        }}

        .topbar-search input:focus {{
            background: #ffffff;
            color: var(--donalu-navy);
            border-color: var(--donalu-yellow);
            box-shadow: 0 0 0 3px rgba(253, 184, 39, 0.35);
        }}

        .topbar-search-icon {{
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 13px;
            color: var(--donalu-yellow);
            pointer-events: none;
        }}

        .topbar-btn-group {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .btn-topbar {{
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 8px 16px;
            border-radius: var(--radius-pill);
            font-size: 12.5px;
            font-weight: 700;
            cursor: pointer;
            border: none;
            transition: all 0.2s;
            text-decoration: none;
            font-family: var(--font-body);
        }}

        .btn-print-pdf {{
            background: var(--donalu-yellow);
            color: var(--donalu-navy);
            box-shadow: 0 4px 12px rgba(253, 184, 39, 0.35);
        }}

        .btn-print-pdf:hover {{
            background: var(--donalu-yellow-dark);
            transform: translateY(-1px);
        }}

        .btn-wa-top {{
            background: var(--donalu-whatsapp);
            color: #ffffff;
        }}

        .btn-feedback-drawer {{
            background: rgba(255, 255, 255, 0.15);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}

        /* === SCREEN PREVIEW INSTRUCTIONS === */
        .preview-instructions-bar {{
            background: #2a2e33;
            color: #e2e8f0;
            padding: 10px 20px;
            text-align: center;
            font-size: 12.5px;
            border-bottom: 1px solid #3e444a;
        }}

        .preview-instructions-bar strong {{
            color: var(--donalu-yellow);
        }}

        /* === EXACT A4 SHEET CONTAINER (PRINT & PDF ENGINE) === */
        .a4-viewport {{
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 30px 15px;
            gap: 30px;
        }}

        .a4-sheet {{
            width: 210mm;
            height: 297mm;
            min-height: 297mm;
            max-height: 297mm;
            background: #ffffff;
            box-sizing: border-box;
            padding: 12mm 14mm 10mm 14mm;
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.35);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
            overflow: hidden;
            page-break-after: always;
            break-after: page;
            page-break-inside: avoid;
            break-inside: avoid;
        }}

        /* === 1. CAPA (FRONT COVER) SHEET === */
        .a4-cover-sheet {{
            background: radial-gradient(circle at 80% 20%, #003ca5 0%, #001f56 50%, #001233 100%);
            color: #ffffff;
            padding: 24mm 20mm;
            border: 3px solid var(--donalu-yellow);
        }}

        .cover-golden-bar {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 12px;
            background: linear-gradient(90deg, #FDB827, #E9A30F, #003CA5, #FDB827);
        }}

        .cover-header-brand {{
            display: flex;
            align-items: center;
            gap: 18px;
        }}

        .cover-logo-big {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: #ffffff;
            padding: 4px;
            box-shadow: 0 0 0 3px var(--donalu-yellow);
        }}

        .cover-company-title {{
            font-family: var(--font-display);
            font-size: 30px;
            font-weight: 800;
            color: #ffffff;
            line-height: 1.1;
        }}

        .cover-company-title span {{
            color: var(--donalu-yellow);
        }}

        .cover-edition-tag {{
            display: inline-block;
            background: rgba(253, 184, 39, 0.2);
            border: 1px solid var(--donalu-yellow);
            color: var(--donalu-yellow);
            padding: 5px 14px;
            border-radius: var(--radius-pill);
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-top: 6px;
        }}

        .cover-main-block {{
            margin: auto 0;
        }}

        .cover-hero-title {{
            font-family: var(--font-display);
            font-size: 44px;
            font-weight: 800;
            line-height: 1.1;
            letter-spacing: -1px;
            color: #ffffff;
            margin-bottom: 20px;
        }}

        .cover-hero-title span {{
            color: var(--donalu-yellow);
            background: linear-gradient(135deg, #FFF4D6, #FDB827);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .cover-lead-p {{
            font-size: 14.5px;
            line-height: 1.65;
            color: #dbeafe;
            margin-bottom: 30px;
            max-width: 170mm;
        }}

        .cover-features-row {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
        }}

        .feat-card {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-left: 4px solid var(--donalu-yellow);
            border-radius: var(--radius-sm);
            padding: 12px 14px;
        }}

        .feat-card-num {{
            font-family: var(--font-mono);
            font-size: 20px;
            font-weight: 800;
            color: var(--donalu-yellow);
        }}

        .feat-card-lbl {{
            font-size: 11px;
            font-weight: 700;
            color: #ffffff;
            text-transform: uppercase;
        }}

        .cover-footer-brand {{
            border-top: 1px solid rgba(255, 255, 255, 0.2);
            padding-top: 18px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            font-size: 12px;
            color: #cbd5e1;
        }}

        .cover-footer-brand strong {{
            color: var(--donalu-yellow);
        }}

        /* === 2. APRESENTAÇÃO & ÍNDICE GERAL SHEET === */
        .a4-toc-sheet {{
            padding: 16mm 16mm 12mm 16mm;
            background: #ffffff;
        }}

        .toc-intro-box {{
            background: #f8fafc;
            border: 1px solid var(--donalu-border);
            border-left: 5px solid var(--donalu-yellow);
            border-radius: var(--radius-md);
            padding: 16px 20px;
            margin-bottom: 18px;
        }}

        .toc-intro-box h2 {{
            font-family: var(--font-display);
            font-size: 20px;
            font-weight: 800;
            color: var(--donalu-navy);
            margin-bottom: 6px;
        }}

        .toc-intro-box p {{
            font-size: 12.5px;
            color: var(--donalu-text-muted);
            line-height: 1.5;
        }}

        .toc-section-title {{
            font-family: var(--font-display);
            font-size: 17px;
            font-weight: 800;
            color: var(--donalu-navy);
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid var(--donalu-navy);
            padding-bottom: 6px;
        }}

        .toc-section-title span {{
            font-size: 11px;
            font-weight: 600;
            color: var(--donalu-text-muted);
            font-family: var(--font-body);
        }}

        .toc-list {{
            display: flex;
            flex-direction: column;
            gap: 9px;
            margin-bottom: auto;
        }}

        .toc-row-card {{
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 10px 14px;
            background: #ffffff;
            border: 1px solid var(--donalu-border);
            border-radius: var(--radius-md);
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }}

        .toc-icon-circle {{
            width: 38px;
            height: 38px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            flex-shrink: 0;
        }}

        .toc-row-details {{
            flex: 1;
        }}

        .toc-row-title {{
            font-size: 13.5px;
            font-weight: 700;
            color: var(--donalu-navy);
            margin-bottom: 2px;
        }}

        .toc-row-desc {{
            font-size: 11.5px;
            color: var(--donalu-text-muted);
            line-height: 1.35;
        }}

        .toc-row-meta {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .toc-count-pill {{
            background: #f1f5f9;
            color: var(--donalu-navy);
            padding: 3px 8px;
            border-radius: var(--radius-sm);
            font-size: 11px;
            font-weight: 700;
        }}

        .toc-page-num {{
            font-family: var(--font-mono);
            font-size: 12px;
            font-weight: 800;
            color: var(--donalu-blue-primary);
            background: var(--donalu-blue-light);
            padding: 3px 8px;
            border-radius: var(--radius-sm);
        }}

        /* === 3. PÁGINAS DE PRODUTO (RUNNING HEAD/FOOT + 2x2 GRID) === */
        .sheet-header {{
            height: 14mm;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 2px solid var(--donalu-navy);
            padding-bottom: 3mm;
            margin-bottom: 4mm;
        }}

        .sheet-header-left {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .sheet-logo-mini {{
            height: 28px;
            width: 28px;
            object-fit: contain;
            border-radius: 50%;
            background: #ffffff;
            box-shadow: 0 0 0 1.5px var(--donalu-yellow);
        }}

        .sheet-brand-name {{
            font-family: var(--font-display);
            font-size: 13px;
            font-weight: 800;
            color: var(--donalu-navy);
            display: block;
            line-height: 1.1;
        }}

        .sheet-brand-sub {{
            font-size: 9.5px;
            color: var(--donalu-text-muted);
            font-weight: 600;
            text-transform: uppercase;
        }}

        .sheet-seg-pill {{
            font-size: 11px;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: var(--radius-pill);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* 2x2 GRID (PERFECT A4 FIT: 2 COLS x 2 ROWS) */
        .sheet-grid-2x2 {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            grid-template-rows: repeat(2, 118mm);
            gap: 5mm;
            height: 243mm;
            box-sizing: border-box;
        }}

        /* PRODUCT CARD INSIDE A4 */
        .a4-product-card {{
            background: #ffffff;
            border: 1px solid var(--donalu-border);
            border-radius: var(--radius-md);
            padding: 10px 12px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 118mm;
            box-sizing: border-box;
            position: relative;
            page-break-inside: avoid;
            break-inside: avoid;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }}

        .a4-product-card:hover {{
            border-color: var(--donalu-blue-primary);
        }}

        .a4-product-card.card-approved {{
            border-color: #22c55e !important;
            box-shadow: 0 0 0 2px #86efac !important;
        }}

        .a4-product-card.card-needs-adjust {{
            border-color: var(--donalu-yellow) !important;
            box-shadow: 0 0 0 2px #fde68a !important;
        }}

        .card-head {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 18px;
            margin-bottom: 2px;
        }}

        .sku-badge {{
            font-family: var(--font-mono);
            font-size: 10.5px;
            font-weight: 800;
            color: var(--donalu-navy);
            background: #f1f5f9;
            padding: 1px 6px;
            border-radius: var(--radius-sm);
        }}

        .card-seg-pill {{
            font-size: 9.5px;
            font-weight: 700;
            padding: 1px 8px;
            border-radius: var(--radius-pill);
        }}

        .feedback-mark-btn {{
            background: transparent;
            border: none;
            cursor: pointer;
            font-size: 14px;
            padding: 0;
            line-height: 1;
        }}

        .card-visual {{
            height: 38mm;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            background: radial-gradient(circle at center, #ffffff 40%, #f8fafc 100%);
            border-radius: var(--radius-sm);
            margin-bottom: 2px;
            overflow: hidden;
        }}

        .packshot-glow {{
            position: absolute;
            bottom: 4px;
            width: 100px;
            height: 10px;
            border-radius: 50%;
            background: radial-gradient(ellipse, rgba(0, 31, 86, 0.12) 0%, rgba(0,0,0,0) 70%);
            pointer-events: none;
        }}

        .packshot-img {{
            max-height: 36mm;
            max-width: 90%;
            object-fit: contain;
            filter: drop-shadow(0 6px 8px rgba(0, 31, 86, 0.12));
            position: relative;
            z-index: 2;
        }}

        .brand-tag {{
            position: absolute;
            bottom: 3px;
            left: 4px;
            background: rgba(0, 31, 86, 0.88);
            color: var(--donalu-yellow);
            font-size: 8.5px;
            font-weight: 800;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            padding: 1px 6px;
            border-radius: 3px;
            z-index: 3;
        }}

        .card-details {{
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            flex: 1;
        }}

        .card-product-name {{
            font-family: var(--font-display);
            font-size: 13.5px;
            font-weight: 800;
            color: var(--donalu-navy);
            line-height: 1.25;
            margin-bottom: 4px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            height: 34px;
        }}

        .specs-mini-table {{
            background: #f8fafc;
            border: 1px solid var(--donalu-border);
            border-radius: var(--radius-sm);
            padding: 5px 8px;
            display: flex;
            flex-direction: column;
            gap: 2.5px;
            margin-bottom: 6px;
            font-size: 10.5px;
        }}

        .spec-mini-row {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            gap: 6px;
            line-height: 1.25;
        }}

        .spec-k {{
            color: #64748b;
            font-size: 9.5px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            flex-shrink: 0;
        }}

        .spec-v {{
            color: #1e293b;
            font-weight: 600;
            text-align: right;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .bold-pkg {{
            color: var(--donalu-navy);
            font-weight: 700;
        }}

        .active-mini-row {{
            border-top: 1px dashed #e2e8f0;
            padding-top: 2px;
            margin-top: 1px;
        }}

        .spec-k-active {{
            color: var(--donalu-blue-primary);
            font-size: 9.5px;
            font-weight: 800;
            text-transform: uppercase;
            flex-shrink: 0;
        }}

        .spec-v-active {{
            color: var(--donalu-blue-dark);
            font-weight: 700;
            text-align: right;
            font-size: 10px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .directions-mini-row {{
            border-top: 1px dashed #e2e8f0;
            padding-top: 2px;
            margin-top: 1px;
        }}

        .directions-clamp {{
            font-size: 9.5px;
            color: #475569;
            font-weight: 500;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            white-space: normal;
            text-align: left;
            line-height: 1.25;
        }}

        .card-btns {{
            display: grid;
            grid-template-columns: 1fr auto auto;
            gap: 4px;
            align-items: center;
        }}

        .btn-card-wa {{
            background: var(--donalu-whatsapp);
            color: #ffffff;
            font-size: 10px;
            font-weight: 700;
            padding: 5px 6px;
            border-radius: var(--radius-sm);
            text-decoration: none;
            text-align: center;
            white-space: nowrap;
        }}

        .btn-card-wa:hover {{
            background: var(--donalu-whatsapp-dark);
        }}

        .btn-card-site {{
            background: #eff6ff;
            color: var(--donalu-blue-primary);
            border: 1px solid #bfdbfe;
            font-size: 10px;
            font-weight: 600;
            padding: 4px 6px;
            border-radius: var(--radius-sm);
            text-decoration: none;
            text-align: center;
            white-space: nowrap;
        }}

        .btn-card-feedback {{
            background: #f1f5f9;
            border: 1px solid var(--donalu-border);
            color: #475569;
            font-size: 10px;
            font-weight: 600;
            padding: 4px 6px;
            border-radius: var(--radius-sm);
            cursor: pointer;
            white-space: nowrap;
        }}

        /* RUNNING FOOTER */
        .sheet-footer {{
            height: 8mm;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-top: 1px solid #cbd5e1;
            padding-top: 2mm;
            font-size: 9.5px;
            color: #64748b;
        }}

        .sheet-footer strong {{
            color: var(--donalu-navy);
        }}

        .sheet-page-counter {{
            font-family: var(--font-mono);
            font-size: 10.5px;
            color: var(--donalu-navy);
        }}

        /* === 4. CONTRA-CAPA (BACK COVER) SHEET === */
        .a4-back-sheet {{
            background: radial-gradient(circle at 20% 80%, #002266 0%, #001f56 50%, #001233 100%);
            color: #ffffff;
            padding: 24mm 20mm;
            border: 3px solid var(--donalu-yellow);
        }}

        .back-logo-img {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: #ffffff;
            padding: 4px;
            box-shadow: 0 0 0 3px var(--donalu-yellow);
            margin-bottom: 12px;
        }}

        .back-brand-title {{
            font-family: var(--font-display);
            font-size: 28px;
            font-weight: 800;
            color: #ffffff;
        }}

        .back-brand-sub {{
            font-size: 12px;
            color: var(--donalu-yellow);
            font-weight: 700;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }}

        .back-panels-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: auto 0;
        }}

        .back-info-panel {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-left: 4px solid var(--donalu-yellow);
            border-radius: var(--radius-md);
            padding: 18px;
        }}

        .back-info-panel h3 {{
            font-family: var(--font-display);
            font-size: 16px;
            font-weight: 700;
            color: var(--donalu-yellow);
            margin-bottom: 12px;
        }}

        .back-data-item {{
            margin-bottom: 10px;
        }}

        .back-data-k {{
            font-size: 9.5px;
            color: #94a3b8;
            text-transform: uppercase;
            font-weight: 700;
        }}

        .back-data-v {{
            font-size: 13px;
            color: #ffffff;
            font-weight: 600;
        }}

        .back-pillars-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 10px;
            font-size: 11.5px;
            color: #cbd5e1;
        }}

        .back-pillars-list li {{
            display: flex;
            align-items: flex-start;
            gap: 8px;
            line-height: 1.4;
        }}

        .check-icon {{
            color: var(--donalu-yellow);
            font-weight: 800;
        }}

        .back-footer-legal {{
            border-top: 1px solid rgba(255, 255, 255, 0.2);
            padding-top: 14px;
            text-align: center;
            font-size: 10.5px;
            color: #94a3b8;
        }}

        /* === MODAL & DRAWER DE FEEDBACK / PALPITES === */
        .modal-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 20, 56, 0.7);
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
            max-width: 500px;
            padding: 24px;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.3);
            border-top: 5px solid var(--donalu-yellow);
        }}

        .modal-title {{
            font-family: var(--font-display);
            font-size: 18px;
            font-weight: 800;
            color: var(--donalu-navy);
            margin-bottom: 4px;
        }}

        .modal-subtitle {{
            font-size: 12px;
            color: var(--donalu-text-muted);
            margin-bottom: 14px;
        }}

        .modal-textarea {{
            width: 100%;
            height: 100px;
            border: 1px solid var(--donalu-border);
            border-radius: var(--radius-sm);
            padding: 10px;
            font-family: var(--font-body);
            font-size: 13px;
            outline: none;
            resize: vertical;
            margin-bottom: 14px;
        }}

        .modal-textarea:focus {{
            border-color: var(--donalu-blue-primary);
            box-shadow: 0 0 0 3px rgba(0, 60, 165, 0.15);
        }}

        .modal-status-select {{
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
        }}

        .status-radio-label {{
            flex: 1;
            padding: 8px;
            border: 1px solid var(--donalu-border);
            border-radius: var(--radius-sm);
            font-size: 12px;
            font-weight: 600;
            text-align: center;
            cursor: pointer;
        }}

        .status-radio-label input {{
            display: none;
        }}

        .status-radio-label:has(input:checked) {{
            border-color: var(--donalu-blue-primary);
            background: var(--donalu-blue-light);
            color: var(--donalu-blue-primary);
        }}

        .modal-actions {{
            display: flex;
            justify-content: flex-end;
            gap: 8px;
        }}

        .drawer-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 20, 56, 0.5);
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
            box-shadow: -10px 0 35px rgba(0, 20, 56, 0.2);
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
            padding: 18px 20px;
            background: var(--donalu-navy);
            color: #ffffff;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid var(--donalu-yellow);
        }}

        .drawer-header h3 {{
            font-family: var(--font-display);
            font-size: 17px;
            font-weight: 800;
            color: #ffffff;
        }}

        .drawer-close-btn {{
            background: transparent;
            border: none;
            font-size: 22px;
            cursor: pointer;
            color: var(--donalu-yellow);
        }}

        .drawer-body {{
            padding: 18px;
            overflow-y: auto;
            flex: 1;
        }}

        .drawer-footer {{
            padding: 14px 18px;
            border-top: 1px solid var(--donalu-border);
            display: flex;
            gap: 8px;
            background: #f8fafc;
        }}

        /* === STRICT A4 PRINT CSS: PREVENTS ANY PRODUCT SLICING === */
        @page {{
            size: A4 portrait;
            margin: 0; /* Zero browser margins: .a4-sheet controls padding milimetrically */
        }}

        @media print {{
            html, body {{
                margin: 0 !important;
                padding: 0 !important;
                background: #ffffff !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }}

            .donalu-topbar,
            .preview-instructions-bar,
            .btn-card-feedback,
            .btn-card-wa,
            .feedback-mark-btn,
            .modal-overlay,
            .drawer-overlay,
            .feedback-drawer,
            .btn-card-site {{
                display: none !important;
            }}

            .a4-viewport {{
                padding: 0 !important;
                gap: 0 !important;
            }}

            .a4-sheet {{
                width: 210mm !important;
                height: 297mm !important;
                min-height: 297mm !important;
                max-height: 297mm !important;
                padding: 12mm 14mm 10mm 14mm !important;
                margin: 0 !important;
                box-shadow: none !important;
                border: none !important;
                page-break-after: always !important;
                break-after: page !important;
                page-break-inside: avoid !important;
                break-inside: avoid !important;
                box-sizing: border-box !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: space-between !important;
                overflow: hidden !important;
            }}

            .a4-cover-sheet {{
                padding: 24mm 20mm !important;
                border: none !important;
            }}

            .a4-back-sheet {{
                padding: 24mm 20mm !important;
                border: none !important;
            }}

            .a4-sheet:last-child {{
                page-break-after: avoid !important;
                break-after: avoid !important;
            }}

            .sheet-grid-2x2 {{
                height: 243mm !important;
                grid-template-rows: repeat(2, 118mm) !important;
            }}

            .a4-product-card {{
                height: 118mm !important;
                box-shadow: none !important;
                border: 1px solid #cbd5e1 !important;
                page-break-inside: avoid !important;
                break-inside: avoid !important;
            }}

            * {{
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }}
        }}
    </style>
</head>
<body>

    <!-- TOPBAR (SCREEN ONLY) -->
    <header class="donalu-topbar">
        <div class="topbar-inner">
            <a href="#" class="topbar-brand">
                <img src="assets_donalu/logo-donalu-128.png" alt="Dona Lu Logo" class="topbar-logo">
                <div>
                    <div class="topbar-brand-title">DONA LU <span>· MATERIAIS</span></div>
                    <div class="topbar-brand-subtitle">Catálogo Oficial A4 / PDF · Start Química</div>
                </div>
            </a>

            <div class="topbar-search">
                <span class="topbar-search-icon">🔍</span>
                <input type="text" id="liveSearch" placeholder="Localizar produto, ativo, embalagem ou fragrância..." oninput="handleSearch()">
            </div>

            <div class="topbar-btn-group">
                <a href="https://wa.me/5517981321919" target="_blank" class="btn-topbar btn-wa-top">
                    <span>💬</span> WhatsApp (17) 98132-1919
                </a>
                <button class="btn-topbar btn-print-pdf" onclick="window.print()">
                    <span>🖨️</span> Salvar em PDF (A4)
                </button>
                <button class="btn-topbar btn-feedback-drawer" onclick="toggleDrawer()">
                    <span>📝</span> Palpites (<span id="feedbackCounter">0</span>)
                </button>
            </div>
        </div>
    </header>

    <div class="preview-instructions-bar">
        📄 <strong>Visualização em Folhas A4 Reais:</strong> Cada folha abaixo representa exatamente 1 página do PDF (com 4 produtos por folha), garantindo que <strong>nenhum produto seja cortado</strong> na quebra de página.
    </div>

    <!-- MAIN A4 VIEWPORT (SHEET BY SHEET) -->
    <main class="a4-viewport">

        <!-- 1. CAPA (FRONT COVER) SHEET -->
        <div class="a4-sheet a4-cover-sheet">
            <div class="cover-golden-bar"></div>

            <div class="cover-header-brand">
                <img src="assets_donalu/logo-donalu-256.png" alt="Dona Lu Logo Oficial" class="cover-logo-big">
                <div>
                    <div class="cover-company-title">DONA LU <span>MATERIAIS</span></div>
                    <span class="cover-edition-tag">EDIÇÃO 2026 / 2027 · CATÁLOGO TÉCNICO</span>
                </div>
            </div>

            <div class="cover-main-block">
                <h1 class="cover-hero-title">
                    Catálogo Oficial de <br><span>Produtos de Limpeza Profissional</span>
                </h1>
                <p class="cover-lead-p">
                    Apresentação completa das linhas saneantes, desengraxantes, desinfetantes, ceras de alto brilho, pós-obra e tratamento de tecidos. Soluções industriais e comerciais distribuídas com assessoria técnica e pronta entrega pela <strong>Dona Lu</strong> em parceria oficial com a <strong>Start Química</strong>.
                </p>

                <div class="cover-features-row">
                    <div class="feat-card">
                        <div class="feat-card-num">80</div>
                        <div class="feat-card-lbl">Produtos Homologados</div>
                    </div>
                    <div class="feat-card">
                        <div class="feat-card-num">07</div>
                        <div class="feat-card-lbl">Linhas Especializadas</div>
                    </div>
                    <div class="feat-card">
                        <div class="feat-card-num">100%</div>
                        <div class="feat-card-lbl">Conformidade Anvisa</div>
                    </div>
                    <div class="feat-card">
                        <div class="feat-card-num">A4</div>
                        <div class="feat-card-lbl">Pronto para Impressão</div>
                    </div>
                </div>
            </div>

            <div class="cover-footer-brand">
                <div>
                    Distribuição & Consultoria Técnica: <strong>Dona Lu Materiais de Limpeza</strong><br>
                    São José do Rio Preto e Região · Telefone / WhatsApp: (17) 98132-1919
                </div>
                <div>
                    Linhas <strong>Azulim · Tuff · Pedrex · Asseptgel · Indy Cryl</strong>
                </div>
            </div>
        </div>

        <!-- 2. APRESENTAÇÃO & ÍNDICE GERAL SHEET -->
        <div class="a4-sheet a4-toc-sheet">
            <header class="sheet-header">
                <div class="sheet-header-left">
                    <img src="assets_donalu/logo-donalu-128.png" alt="Dona Lu" class="sheet-logo-mini">
                    <div class="sheet-header-brand">
                        <span class="sheet-brand-name">DONA LU · MATERIAIS DE LIMPEZA</span>
                        <span class="sheet-brand-sub">Distribuidora Autorizada Start Química</span>
                    </div>
                </div>
                <div class="sheet-header-right">
                    <span class="sheet-seg-pill" style="background:#f1f5f9; color:#1e293b; border:1px solid #cbd5e1;">Sumário Geral</span>
                </div>
            </header>

            <div class="toc-intro-box">
                <h2>Soluções que Fazem a Diferença no seu Negócio</h2>
                <p>
                    A <strong>Dona Lu</strong> é a distribuidora de referência em produtos de limpeza profissional em São José do Rio Preto e região. Oferecemos consultoria para redução do custo por metro quadrado limpo com diluição inteligente, além de soluções para pós-obra, empresas, condomínios e locação de máquinas de limpeza.
                </p>
            </div>

            <div class="toc-section-title">
                Índice de Linhas e Segmentos <span>Portfólio com 80 produtos</span>
            </div>

            <div class="toc-list">
                {''.join(toc_items)}
            </div>

            <footer class="sheet-footer">
                <div class="sheet-footer-left">
                    <span>Central de Atendimento: <strong>(17) 98132-1919</strong> · donalumateriais@gmail.com</span>
                </div>
                <div class="sheet-footer-right">
                    <span class="sheet-page-counter">Sumário</span>
                </div>
            </footer>
        </div>

        <!-- 3. PÁGINAS DE PRODUTO (PÁGINAS 01 A 20) -->
        {''.join(rendered_product_sheets)}

        <!-- 4. CONTRA-CAPA (BACK COVER) SHEET -->
        <div class="a4-sheet a4-back-sheet">
            <div class="cover-golden-bar"></div>

            <div style="text-align: center;">
                <img src="assets_donalu/logo-donalu-256.png" alt="Dona Lu Logo" class="back-logo-img">
                <div class="back-brand-title">DONA LU MATERIAIS DE LIMPEZA</div>
                <div class="back-brand-sub">Distribuição Autorizada Start Química</div>
            </div>

            <div class="back-panels-grid">
                <div class="back-info-panel">
                    <h3>📞 Central de Atendimento & Pedidos</h3>
                    
                    <div class="back-data-item">
                        <div class="back-data-k">Razão Social:</div>
                        <div class="back-data-v">Dona Lu Materiais de Limpeza</div>
                    </div>

                    <div class="back-data-item">
                        <div class="back-data-k">CNPJ:</div>
                        <div class="back-data-v">69.236.751/0001-08</div>
                    </div>

                    <div class="back-data-item">
                        <div class="back-data-k">WhatsApp / Comercial:</div>
                        <div class="back-data-v">(17) 98132-1919</div>
                    </div>

                    <div class="back-data-item">
                        <div class="back-data-k">E-mail:</div>
                        <div class="back-data-v">donalumateriais@gmail.com</div>
                    </div>

                    <div class="back-data-item">
                        <div class="back-data-k">Horário:</div>
                        <div class="back-data-v">Seg a Sex: 8h às 18h | Sáb: 8h às 12h</div>
                    </div>

                    <div class="back-data-item">
                        <div class="back-data-k">Cidade / Região:</div>
                        <div class="back-data-v">São José do Rio Preto - SP</div>
                    </div>
                </div>

                <div class="back-info-panel">
                    <h3 style="color:#ffffff;">Diferenciais & Suporte Técnico</h3>
                    <ul class="back-pillars-list">
                        <li><span class="check-icon">✓</span> <strong>Consultoria de Diluição:</strong> Auxiliamos na escolha da proporção ideal para diminuir o custo por aplicação.</li>
                        <li><span class="check-icon">✓</span> <strong>Especialistas em Pós-Obra:</strong> Produtos específicos para remoção de cimento, rejunte e ceras antigas.</li>
                        <li><span class="check-icon">✓</span> <strong>Parceria Oficial Start Química:</strong> Fórmulas certificadas pela ANVISA e suporte técnico do fabricante.</li>
                        <li><span class="check-icon">✓</span> <strong>Locação de Máquinas:</strong> Enceradeiras, lavadoras de piso e extratoras profissionais.</li>
                        <li><span class="check-icon">✓</span> <strong>Entrega Programada:</strong> Fornecimento contínuo para condomínios, escolas e empresas.</li>
                    </ul>
                </div>
            </div>

            <div class="back-footer-legal">
                <p>&copy; 2026 Dona Lu Materiais de Limpeza · CNPJ 69.236.751/0001-08 · Distribuidora Oficial Start Química.<br>
                Catálogo técnico diagramado e paginado para impressão gráfica e exportação em PDF A4.</p>
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

            <textarea id="modalCommentText" class="modal-textarea" placeholder="Ex: Mudar o volume principal, enfatizar a embalagem de 5L, ajustar indicação..."></textarea>
            
            <div class="modal-actions">
                <button class="btn-topbar" style="background:#e2e8f0; color:#334155;" onclick="closeCommentModal()">Cancelar</button>
                <button class="btn-topbar btn-print-pdf" onclick="saveProductComment()">Salvar Palpite</button>
            </div>
        </div>
    </div>

    <!-- DRAWER LATERAL DE FEEDBACKS -->
    <div class="drawer-overlay" id="drawerOverlay" onclick="toggleDrawer()"></div>
    <div class="feedback-drawer" id="feedbackDrawer">
        <div class="drawer-header">
            <h3>📝 Painel de Palpites & Feedback</h3>
            <button class="drawer-close-btn" onclick="toggleDrawer()">&times;</button>
        </div>
        <div class="drawer-body" id="drawerList">
            <p style="color: #64748b; font-size: 13.5px;">Nenhum palpite registrado ainda. Clique no botão "💬 Palpite" em qualquer produto ou marque as bolinhas para aprovar/ajustar.</p>
        </div>
        <div class="drawer-footer">
            <button class="btn-topbar btn-print-pdf" style="flex:1;" onclick="copyFeedbackToClipboard()">📋 Copiar Resumo dos Palpites</button>
            <button class="btn-topbar" style="background:#f1f5f9; color:#475569;" onclick="clearAllFeedbacks()">Limpar</button>
        </div>
    </div>

    <script>
        let feedbackData = JSON.parse(localStorage.getItem('donalu_catalog_feedbacks_a4') || '{{}}');
        let currentModalProductId = null;

        function updateFeedbackUI() {{
            const keys = Object.keys(feedbackData);
            document.getElementById('feedbackCounter').innerText = keys.length;

            document.querySelectorAll('.a4-product-card').forEach(card => {{
                card.classList.remove('card-approved', 'card-needs-adjust');
                const btn = card.querySelector('.feedback-mark-btn');
                if (btn) btn.innerText = '⚪';
            }});

            const drawerList = document.getElementById('drawerList');
            if (keys.length === 0) {{
                drawerList.innerHTML = '<p style="color: #64748b; font-size: 13.5px; text-align:center; padding: 30px 10px;">Nenhum palpite ou anotação registrada ainda.<br><br>💡 Você ou quem estiver revisando podem clicar em <strong>"💬 Palpite"</strong> nos produtos para sugerir mudanças de texto, foto ou embalagem.</p>';
                return;
            }}

            let listHtml = '';
            keys.forEach(id => {{
                const item = feedbackData[id];
                const card = document.querySelector(`.a4-product-card[data-id="${{id}}"]`);
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
                        <p style="font-size:12.5px; color:#334155; line-height:1.4;">${{item.comment ? item.comment : '<em>Sem observação de texto</em>'}}</p>
                        <div style="text-align:right; margin-top:8px;">
                            <button onclick="removeFeedback(${{id}})" style="background:none; border:none; color:#ef4444; font-size:11px; cursor:pointer;">Remover</button>
                        </div>
                    </div>
                `;
            }});
            drawerList.innerHTML = listHtml;
            localStorage.setItem('donalu_catalog_feedbacks_a4', JSON.stringify(feedbackData));
        }}

        function toggleApproval(id) {{
            const card = document.querySelector(`.a4-product-card[data-id="${{id}}"]`);
            const title = card.querySelector('.card-product-name').innerText;
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
            const card = document.querySelector(`.a4-product-card[data-id="${{id}}"]`);
            const title = card.querySelector('.card-product-name').innerText;
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
            const card = document.querySelector(`.a4-product-card[data-id="${{currentModalProductId}}"]`);
            const title = card.querySelector('.card-product-name').innerText;
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
            let text = '=== PALPITES & FEEDBACK DO CATÁLOGO DONA LU ===\\n\\n';
            keys.forEach(id => {{
                const item = feedbackData[id];
                const statusStr = item.status === 'approved' ? '[APROVADO]' : '[AJUSTE SUGERIDO]';
                text += `#${{String(id).padStart(3, '0')}} - ${{item.name}}\\nStatus: ${{statusStr}}\\n`;
                if (item.comment) text += `Observação: ${{item.comment}}\\n`;
                text += '-------------------------------------\\n';
            }});
            navigator.clipboard.writeText(text).then(() => {{
                alert('Resumo dos palpites copiado para a área de transferência! Pode colar no WhatsApp ou enviar por e-mail.');
            }});
        }}

        // Live Search Filter (Highlights matching cards across pages)
        function handleSearch() {{
            const q = document.getElementById('liveSearch').value.toLowerCase().trim();
            const cards = document.querySelectorAll('.a4-product-card');
            cards.forEach(card => {{
                const name = card.getAttribute('data-name');
                const active = card.getAttribute('data-active');
                const frag = card.getAttribute('data-fragrance');
                const brand = card.getAttribute('data-brand');
                const text = card.innerText.toLowerCase();
                if (!q || name.includes(q) || active.includes(q) || frag.includes(q) || brand.includes(q) || text.includes(q)) {{
                    card.style.opacity = '1';
                    card.style.filter = 'none';
                }} else {{
                    card.style.opacity = '0.25';
                    card.style.filter = 'grayscale(80%)';
                }}
            }});
        }}

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

print("Novo catálogo diagramado em folhas A4 reais gerado com sucesso!")

