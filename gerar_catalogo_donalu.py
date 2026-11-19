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
        "desc": "Soluções profissionais para pós-obra, restauração, proteção e acabamento de pedras rústicas, cerâmicas, porcelanatos, ardósias e pisos vinílicos."
    },
    "Desinfecção e Limpeza Geral Multiuso": {
        "icon": "✨",
        "bg": "#e0f2fe",
        "text": "#075985",
        "border": "#bae6fd",
        "color": "#0284c7",
        "badge_bg": "#f0f9ff",
        "short": "Limpeza Geral",
        "desc": "Alto poder bactericida e ação desengordurante profunda para manutenção diária e pesada em empresas, condomínios, residências e indústrias."
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
        "desc": "Linha Asseptgel com eficácia comprovada contra germes e bactérias, álcool 70º hidratante, sabonetes antissépticos e cuidados com a pele."
    },
    "Automotivo e Oficinas": {
        "icon": "🚗",
        "bg": "#f1f5f9",
        "text": "#1e293b",
        "border": "#cbd5e1",
        "color": "#475569",
        "badge_bg": "#f8fafc",
        "short": "Linha Automotiva",
        "desc": "Estética automotiva profissional: revitalização de pneus, silicones puros, hidratação de couros, ceras de alto brilho e desengraxantes."
    },
    "Aromatização e Cuidados Pet": {
        "icon": "🌸",
        "bg": "#fae8ff",
        "text": "#86198f",
        "border": "#f5d0fe",
        "color": "#c026d3",
        "badge_bg": "#fdf4ff",
        "short": "Aromatizantes & Pet",
        "desc": "Fragrâncias finas e neutralizadores biológicos de odores para transformar ambientes corporativos, condomínios e lares com animais de estimação."
    }
}

# Group products by segment
by_segment = {}
for p in products:
    seg = p['segment']
    if seg not in by_segment:
        by_segment[seg] = []
    by_segment[seg].append(p)

def render_product_card(p):
    safe_png = f"imagens_produtos/{p['png_file'].replace('%', '%25')}"
    seg_info = SEGMENT_STYLES.get(p['segment'], {
        "icon": "📦", "bg": "#f8fafc", "text": "#334155", "border": "#e2e8f0", "color": "#003CA5", "badge_bg": "#fff", "short": "Geral"
    })
    
    # Packaging badges
    pkg_list = [x.strip() for x in p['packaging'].split(',') if x.strip()]
    pkg_badges = "".join([f'<span class="spec-pill pkg-pill">{pkg}</span>' for pkg in pkg_list])
    
    # Fragrance badges
    frag_list = [x.strip() for x in p['fragrance'].split(',') if x.strip()]
    frag_badges = "".join([f'<span class="spec-pill frag-pill"><span class="pill-dot"></span> {f}</span>' for f in frag_list])
    
    # Surfaces tag
    surfaces = p.get('surfaces', '')
    surf_html = f'<div class="card-spec-row"><span class="spec-label">Superfícies:</span> <span class="spec-val-surface">{surfaces}</span></div>' if surfaces else ''
    
    # WhatsApp request link
    wa_msg = urllib.parse.quote(f"Olá Dona Lu! Tenho interesse no produto: {p['name']} (Item #{p['index']:03d}). Poderia me passar um orçamento/informações?")
    wa_btn = f'<a href="https://wa.me/5517981321919?text={wa_msg}" target="_blank" class="btn-wa-card" title="Pedir Orçamento no WhatsApp"><span>Pedir no WhatsApp</span></a>'
    
    ficha_btn = f'<a href="{p["product_url"]}" target="_blank" class="btn-site-card" title="Ver no portal do fabricante">Ficha Técnica &rarr;</a>'
    
    return f"""
    <div class="product-card" 
         data-id="{p['index']}" 
         data-segment="{p['segment']}" 
         data-name="{p['name'].lower()}" 
         data-active="{p['active'].lower()}" 
         data-fragrance="{p['fragrance'].lower()}"
         data-brand="{p['brand'].lower()}">
        
        <div class="card-top-bar">
            <span class="card-sku">ITEM #{p['index']:03d}</span>
            <span class="card-segment-tag" style="background:{seg_info['badge_bg']}; color:{seg_info['text']}; border: 1px solid {seg_info['border']};">
                {seg_info['icon']} {seg_info['short']}
            </span>
            <button class="feedback-mark-btn" onclick="toggleApproval({p['index']})" title="Marcar status / Feedback" id="btn-status-{p['index']}">
                ⚪
            </button>
        </div>

        <div class="card-img-stage">
            <div class="pedestal-glow"></div>
            <img src="{safe_png}" alt="{p['name']}" loading="lazy" class="card-img" onerror="this.onerror=null; this.src='{safe_png.replace('%25', '%')}';">
            <div class="card-brand-pill">{p['brand']}</div>
        </div>

        <div class="card-body">
            <div class="card-title-group">
                <h3 class="product-title">{p['name']}</h3>
                <p class="product-desc">{p['description']}</p>
            </div>
            
            <div class="specs-box">
                <div class="card-spec-row">
                    <span class="spec-label">Embalagens / Volumes:</span>
                    <div class="pills-flex">{pkg_badges}</div>
                </div>

                <div class="card-spec-row">
                    <span class="spec-label">Fragrância:</span>
                    <div class="pills-flex">{frag_badges}</div>
                </div>

                <div class="card-spec-row active-ingredient-box">
                    <span class="spec-label-active">Princípio Ativo:</span>
                    <span class="spec-val-active">🧪 {p['active']}</span>
                </div>

                <div class="card-spec-row directions-box">
                    <span class="spec-label">Indicação de Uso:</span>
                    <span class="spec-val-directions">{p['directions']}</span>
                </div>
                
                {surf_html}
            </div>

            <div class="card-actions-row">
                {wa_btn}
                {ficha_btn}
                <button class="btn-comment-card" onclick="openCommentModal({p['index']})" title="Adicionar palpite">💬 Palpite</button>
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
        <a href="#{anchor_id}" class="toc-tile">
            <div class="toc-tile-icon" style="background:{seg_info['bg']}; color:{seg_info['text']}; border: 1px solid {seg_info['border']};">
                {seg_info['icon']}
            </div>
            <div class="toc-tile-text">
                <h4>{seg_name}</h4>
                <span>{len(p_list)} soluções homologadas</span>
            </div>
            <div class="toc-tile-arrow">&rarr;</div>
        </a>
    """)
    
    cards_html = "\n".join([render_product_card(p) for p in p_list])
    
    segments_html.append(f"""
    <section class="catalog-segment-block" id="{anchor_id}">
        <div class="segment-banner" style="border-top: 5px solid {seg_info['color']};">
            <div class="seg-banner-header">
                <div class="seg-banner-badge" style="background:{seg_info['bg']}; color:{seg_info['text']}; border: 1px solid {seg_info['border']};">
                    {seg_info['icon']} {seg_name}
                </div>
                <div class="seg-banner-count">{len(p_list)} produtos</div>
            </div>
            <h2 class="seg-banner-title">{seg_name}</h2>
            <p class="seg-banner-desc">{seg_info['desc']}</p>
        </div>
        
        <div class="products-grid-layout">
            {cards_html}
        </div>
    </section>
    """)

# Full HTML template with Dona Lu styling
html_output = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo Oficial de Produtos — Dona Lu | Limpeza Profissional</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=Montserrat:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
    <link rel="icon" type="image/png" href="assets_donalu/logo-donalu-128.png">
    
    <style>
        /* === DONA LU BRAND TOKENS & SYSTEM === */
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
            --donalu-bg:            #F8FAFC;
            --donalu-card-bg:       #FFFFFF;
            --donalu-surface:       #EFEFEF;
            --donalu-text:          #162239;
            --donalu-text-muted:    #5A6A88;
            --donalu-border:        #E2E8F0;
            --donalu-border-hover:  #CBD5E1;
            
            --font-display: 'Bricolage Grotesque', 'Montserrat', sans-serif;
            --font-body:    'Montserrat', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            --font-mono:    'JetBrains Mono', monospace;
            
            --radius-sm: 6px;
            --radius-md: 12px;
            --radius-lg: 20px;
            --radius-xl: 28px;
            --radius-pill: 9999px;
            
            --shadow-subtle: 0 4px 6px -1px rgba(0, 31, 86, 0.04), 0 2px 4px -2px rgba(0, 31, 86, 0.03);
            --shadow-card:   0 10px 25px -5px rgba(0, 31, 86, 0.07), 0 8px 10px -6px rgba(0, 31, 86, 0.04);
            --shadow-hover:  0 20px 30px -10px rgba(0, 60, 165, 0.14), 0 10px 15px -5px rgba(0, 31, 86, 0.06);
            --shadow-gold:   0 10px 25px -5px rgba(253, 184, 39, 0.35);
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
            line-height: 1.55;
            overflow-x: hidden;
        }}

        /* === TOP STICKY BAR (BRANDED HEADER & PALPITES CONTROLS) === */
        .donalu-topbar {{
            position: sticky;
            top: 0;
            z-index: 1000;
            background: rgba(0, 31, 86, 0.96);
            backdrop-filter: blur(14px);
            border-bottom: 2px solid var(--donalu-yellow);
            box-shadow: 0 10px 30px rgba(0, 20, 56, 0.25);
            padding: 10px 24px;
            color: #ffffff;
        }}

        .topbar-container {{
            max-width: 1440px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
        }}

        .brand-identity {{
            display: flex;
            align-items: center;
            gap: 14px;
            text-decoration: none;
            color: inherit;
        }}

        .brand-logo-img {{
            height: 44px;
            width: 44px;
            object-fit: contain;
            background: #ffffff;
            border-radius: 50%;
            padding: 2px;
            box-shadow: 0 0 0 2px var(--donalu-yellow);
        }}

        .brand-text-block {{
            display: flex;
            flex-direction: column;
        }}

        .brand-name {{
            font-family: var(--font-display);
            font-size: 20px;
            font-weight: 800;
            letter-spacing: -0.5px;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .brand-name-accent {{
            color: var(--donalu-yellow);
        }}

        .brand-subtext {{
            font-size: 11px;
            font-weight: 600;
            color: #b8c4dc;
            letter-spacing: 0.8px;
            text-transform: uppercase;
        }}

        .topbar-search-wrap {{
            flex: 1;
            max-width: 460px;
            position: relative;
        }}

        .topbar-search-input {{
            width: 100%;
            padding: 10px 18px 10px 42px;
            border-radius: var(--radius-pill);
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
            font-family: var(--font-body);
            font-size: 13.5px;
            outline: none;
            transition: all 0.25s;
        }}

        .topbar-search-input::placeholder {{
            color: #b8c4dc;
        }}

        .topbar-search-input:focus {{
            background: #ffffff;
            color: var(--donalu-navy);
            border-color: var(--donalu-yellow);
            box-shadow: 0 0 0 3px rgba(253, 184, 39, 0.35);
        }}

        .topbar-search-input:focus::placeholder {{
            color: #64748b;
        }}

        .search-lens-icon {{
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 14px;
            pointer-events: none;
            color: var(--donalu-yellow);
        }}

        .topbar-actions {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .btn-topbar {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 9px 18px;
            border-radius: var(--radius-pill);
            font-family: var(--font-body);
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            border: none;
            transition: all 0.2s;
            text-decoration: none;
        }}

        .btn-topbar-print {{
            background: var(--donalu-yellow);
            color: var(--donalu-navy);
            box-shadow: 0 4px 12px rgba(253, 184, 39, 0.3);
        }}

        .btn-topbar-print:hover {{
            background: var(--donalu-yellow-dark);
            transform: translateY(-1px);
        }}

        .btn-topbar-feedback {{
            background: rgba(255, 255, 255, 0.12);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.25);
        }}

        .btn-topbar-feedback:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}

        .btn-topbar-whatsapp {{
            background: var(--donalu-whatsapp);
            color: #ffffff;
            box-shadow: 0 4px 12px rgba(37, 211, 102, 0.25);
        }}

        .btn-topbar-whatsapp:hover {{
            background: var(--donalu-whatsapp-dark);
            transform: translateY(-1px);
        }}

        /* === SEGMENT FILTER PILLS === */
        .filter-ribbon {{
            background: #ffffff;
            border-bottom: 1px solid var(--donalu-border);
            padding: 10px 24px;
            overflow-x: auto;
            white-space: nowrap;
        }}

        .filter-ribbon-inner {{
            max-width: 1440px;
            margin: 0 auto;
            display: flex;
            gap: 8px;
            align-items: center;
        }}

        .filter-btn {{
            padding: 7px 16px;
            border-radius: var(--radius-pill);
            font-size: 13px;
            font-weight: 600;
            background: #f1f5f9;
            color: var(--donalu-text);
            border: 1px solid transparent;
            cursor: pointer;
            transition: all 0.2s;
            font-family: var(--font-body);
        }}

        .filter-btn:hover {{
            background: #e2e8f0;
        }}

        .filter-btn.active {{
            background: var(--donalu-navy);
            color: var(--donalu-yellow);
            border-color: var(--donalu-navy);
            box-shadow: 0 2px 8px rgba(0, 31, 86, 0.2);
        }}

        .filter-btn.active .btn-counter {{
            background: var(--donalu-yellow);
            color: var(--donalu-navy);
        }}

        .btn-counter {{
            background: #cbd5e1;
            color: #1e293b;
            padding: 1px 7px;
            border-radius: 12px;
            font-size: 11px;
            margin-left: 5px;
            font-weight: 700;
        }}

        /* === MAIN CATALOG CONTAINER === */
        .catalog-viewport {{
            max-width: 1440px;
            margin: 0 auto;
            padding: 36px 24px 60px 24px;
        }}

        /* === 1. CAPA PRINCIPAL (DONA LU FRONT COVER) === */
        .donalu-cover {{
            min-height: 90vh;
            background: radial-gradient(circle at 80% 20%, #003ca5 0%, #001f56 50%, #001233 100%);
            border-radius: var(--radius-xl);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 60px;
            color: #ffffff;
            box-shadow: 0 25px 60px -15px rgba(0, 20, 56, 0.45);
            margin-bottom: 50px;
            page-break-after: always;
            break-after: page;
            border: 2px solid rgba(253, 184, 39, 0.3);
        }}

        .cover-accent-halo {{
            position: absolute;
            top: -160px;
            right: -160px;
            width: 700px;
            height: 700px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(253, 184, 39, 0.22) 0%, rgba(0, 31, 86, 0) 70%);
            pointer-events: none;
        }}

        .cover-golden-stripe {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 10px;
            background: linear-gradient(90deg, #FDB827, #E9A30F, #003CA5, #FDB827);
        }}

        .cover-top-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
            z-index: 2;
            flex-wrap: wrap;
            gap: 20px;
        }}

        .cover-brand-showcase {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}

        .cover-main-logo {{
            width: 90px;
            height: 90px;
            border-radius: 50%;
            object-fit: contain;
            background: #ffffff;
            padding: 4px;
            box-shadow: 0 0 0 4px var(--donalu-yellow), 0 10px 25px rgba(0, 0, 0, 0.3);
        }}

        .cover-title-lockup {{
            display: flex;
            flex-direction: column;
        }}

        .cover-company-name {{
            font-family: var(--font-display);
            font-size: 34px;
            font-weight: 800;
            letter-spacing: -0.5px;
            color: #ffffff;
            line-height: 1.1;
        }}

        .cover-company-name span {{
            color: var(--donalu-yellow);
        }}

        .cover-company-tag {{
            font-size: 13px;
            font-weight: 600;
            color: var(--donalu-yellow-light);
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-top: 4px;
        }}

        .cover-badge-edition {{
            background: rgba(253, 184, 39, 0.15);
            border: 1.5px solid var(--donalu-yellow);
            color: var(--donalu-yellow);
            padding: 10px 22px;
            border-radius: var(--radius-pill);
            font-weight: 800;
            font-size: 13px;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            backdrop-filter: blur(8px);
        }}

        .cover-center-editorial {{
            position: relative;
            z-index: 2;
            margin: 40px 0;
            max-width: 900px;
        }}

        .cover-label-pill {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(253, 184, 39, 0.2);
            color: #fffbeb;
            border: 1px solid rgba(253, 184, 39, 0.5);
            padding: 6px 16px;
            border-radius: var(--radius-pill);
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            margin-bottom: 24px;
        }}

        .cover-hero-headline {{
            font-family: var(--font-display);
            font-size: 56px;
            font-weight: 800;
            line-height: 1.08;
            letter-spacing: -1.5px;
            color: #ffffff;
            margin-bottom: 24px;
        }}

        .cover-hero-headline .highlight {{
            color: var(--donalu-yellow);
            background: linear-gradient(135deg, #FFF4D6 0%, #FDB827 50%, #E9A30F 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .cover-hero-lead {{
            font-size: 18px;
            line-height: 1.65;
            color: #dbeafe;
            max-width: 760px;
            margin-bottom: 36px;
            font-weight: 400;
        }}

        .cover-metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }}

        .cover-metric-card {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: var(--radius-md);
            padding: 18px;
            backdrop-filter: blur(8px);
            border-left: 4px solid var(--donalu-yellow);
        }}

        .metric-big {{
            font-family: var(--font-mono);
            font-size: 26px;
            font-weight: 800;
            color: var(--donalu-yellow);
            margin-bottom: 4px;
        }}

        .metric-caption {{
            font-size: 13px;
            font-weight: 700;
            color: #ffffff;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .cover-bottom-bar {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            border-top: 1px solid rgba(255, 255, 255, 0.18);
            padding-top: 24px;
            position: relative;
            z-index: 2;
            flex-wrap: wrap;
            gap: 20px;
        }}

        .cover-distrib-info {{
            font-size: 14px;
            color: #cbd5e1;
        }}

        .cover-distrib-info strong {{
            color: var(--donalu-yellow);
            font-size: 15px;
        }}

        .cover-seals-flex {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }}

        .cover-seal-pill {{
            background: rgba(0, 20, 56, 0.5);
            border: 1px solid rgba(253, 184, 39, 0.4);
            padding: 7px 14px;
            border-radius: var(--radius-sm);
            font-size: 12px;
            color: #f8fafc;
            font-weight: 600;
        }}

        /* === 2. APRESENTAÇÃO DONA LU & ÍNDICE === */
        .donalu-about-toc {{
            background: #ffffff;
            border-radius: var(--radius-xl);
            border: 1px solid var(--donalu-border);
            padding: 44px;
            margin-bottom: 50px;
            box-shadow: var(--shadow-card);
            page-break-after: always;
            break-after: page;
        }}

        .about-grid-lead {{
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 40px;
            margin-bottom: 44px;
            padding-bottom: 36px;
            border-bottom: 1px solid var(--donalu-border);
        }}

        .about-lead-text h2 {{
            font-family: var(--font-display);
            font-size: 30px;
            font-weight: 800;
            color: var(--donalu-navy);
            margin-bottom: 12px;
            line-height: 1.2;
        }}

        .about-lead-text p {{
            font-size: 15px;
            color: var(--donalu-text-muted);
            line-height: 1.7;
            margin-bottom: 14px;
        }}

        .about-contact-quickbox {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: var(--radius-lg);
            padding: 24px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            border-left: 5px solid var(--donalu-yellow);
        }}

        .quickbox-item {{
            margin-bottom: 12px;
        }}

        .quickbox-label {{
            font-size: 11px;
            text-transform: uppercase;
            font-weight: 700;
            color: #64748b;
            letter-spacing: 0.5px;
        }}

        .quickbox-val {{
            font-size: 14px;
            font-weight: 700;
            color: var(--donalu-navy);
        }}

        .toc-title-row {{
            text-align: center;
            margin-bottom: 28px;
        }}

        .toc-title-row h3 {{
            font-family: var(--font-display);
            font-size: 24px;
            font-weight: 800;
            color: var(--donalu-navy);
        }}

        .toc-tiles-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
            gap: 16px;
        }}

        .toc-tile {{
            display: flex;
            align-items: center;
            gap: 16px;
            background: #f8fafc;
            border: 1px solid var(--donalu-border);
            border-radius: var(--radius-md);
            padding: 16px 20px;
            text-decoration: none;
            color: inherit;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        .toc-tile:hover {{
            background: #ffffff;
            border-color: var(--donalu-blue-primary);
            box-shadow: var(--shadow-card);
            transform: translateY(-3px);
        }}

        .toc-tile-icon {{
            width: 48px;
            height: 48px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            flex-shrink: 0;
        }}

        .toc-tile-text h4 {{
            font-size: 14px;
            font-weight: 700;
            color: var(--donalu-navy);
            margin-bottom: 2px;
        }}

        .toc-tile-text span {{
            font-size: 12px;
            color: var(--donalu-text-muted);
            font-weight: 500;
        }}

        .toc-tile-arrow {{
            margin-left: auto;
            color: #94a3b8;
            font-weight: 800;
            transition: transform 0.2s;
        }}

        .toc-tile:hover .toc-tile-arrow {{
            color: var(--donalu-blue-primary);
            transform: translateX(4px);
        }}

        /* === 3. SEGMENTOS & GRID DE PRODUTOS === */
        .catalog-segment-block {{
            margin-bottom: 60px;
        }}

        .segment-banner {{
            background: #ffffff;
            border-radius: var(--radius-lg);
            padding: 26px 32px;
            margin-bottom: 24px;
            box-shadow: var(--shadow-subtle);
            border: 1px solid var(--donalu-border);
            border-top-width: 5px !important;
        }}

        .seg-banner-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }}

        .seg-banner-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            font-weight: 700;
            padding: 4px 12px;
            border-radius: var(--radius-pill);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .seg-banner-count {{
            font-family: var(--font-mono);
            font-size: 13px;
            font-weight: 700;
            color: var(--donalu-text-muted);
        }}

        .seg-banner-title {{
            font-family: var(--font-display);
            font-size: 26px;
            font-weight: 800;
            color: var(--donalu-navy);
            margin-bottom: 6px;
        }}

        .seg-banner-desc {{
            font-size: 14px;
            color: var(--donalu-text-muted);
            max-width: 950px;
            line-height: 1.6;
        }}

        .products-grid-layout {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 24px;
        }}

        /* === PRODUCT CARD DESIGN === */
        .product-card {{
            background: #ffffff;
            border: 1px solid var(--donalu-border);
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
            transform: translateY(-6px);
            box-shadow: var(--shadow-hover);
            border-color: var(--donalu-border-hover);
        }}

        .product-card.card-approved {{
            border-color: #22c55e;
            box-shadow: 0 0 0 2px #86efac;
        }}

        .product-card.card-needs-adjust {{
            border-color: var(--donalu-yellow);
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
            font-size: 11.5px;
            font-weight: 700;
            color: var(--donalu-navy);
            background: #f1f5f9;
            padding: 2px 8px;
            border-radius: var(--radius-sm);
        }}

        .card-segment-tag {{
            font-size: 11px;
            font-weight: 700;
            padding: 2px 10px;
            border-radius: var(--radius-pill);
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
            transform: scale(1.25);
        }}

        .card-img-stage {{
            height: 230px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 18px;
            background: radial-gradient(circle at center, #ffffff 45%, #f1f5f9 100%);
            position: relative;
            border-bottom: 1px solid #f1f5f9;
            overflow: hidden;
        }}

        .pedestal-glow {{
            position: absolute;
            bottom: 15px;
            width: 140px;
            height: 18px;
            border-radius: 50%;
            background: radial-gradient(ellipse, rgba(0, 31, 86, 0.15) 0%, rgba(0, 0, 0, 0) 70%);
            pointer-events: none;
        }}

        .card-img {{
            max-height: 100%;
            max-width: 100%;
            object-fit: contain;
            filter: drop-shadow(0 10px 14px rgba(0, 31, 86, 0.1));
            transition: transform 0.3s;
            position: relative;
            z-index: 2;
        }}

        .product-card:hover .card-img {{
            transform: scale(1.06);
        }}

        .card-brand-pill {{
            position: absolute;
            bottom: 8px;
            left: 12px;
            background: rgba(0, 31, 86, 0.9);
            color: var(--donalu-yellow);
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.6px;
            text-transform: uppercase;
            padding: 2px 8px;
            border-radius: var(--radius-sm);
            backdrop-filter: blur(4px);
            z-index: 3;
        }}

        .card-body {{
            padding: 18px;
            display: flex;
            flex-direction: column;
            flex: 1;
            justify-content: space-between;
        }}

        .card-title-group {{
            margin-bottom: 14px;
        }}

        .product-title {{
            font-family: var(--font-display);
            font-size: 16.5px;
            font-weight: 700;
            color: var(--donalu-navy);
            margin-bottom: 6px;
            line-height: 1.35;
        }}

        .product-desc {{
            font-size: 12.5px;
            color: var(--donalu-text-muted);
            line-height: 1.5;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .specs-box {{
            background: #f8fafc;
            border: 1px solid var(--donalu-border);
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

        .pills-flex {{
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
            color: var(--donalu-navy);
        }}

        .frag-pill {{
            background: #fffbeb;
            border: 1px solid #fde68a;
            color: #b45309;
        }}

        .pill-dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--donalu-yellow-dark);
        }}

        .active-ingredient-box {{
            border-top: 1px dashed var(--donalu-border);
            padding-top: 6px;
        }}

        .spec-label-active {{
            font-size: 10.5px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--donalu-blue-primary);
        }}

        .spec-val-active {{
            font-weight: 600;
            color: var(--donalu-blue-dark);
            font-size: 11.5px;
            line-height: 1.35;
        }}

        .directions-box {{
            border-top: 1px dashed var(--donalu-border);
            padding-top: 6px;
        }}

        .spec-val-directions {{
            color: #475569;
            font-size: 11px;
            line-height: 1.45;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .spec-val-surface {{
            color: #334155;
            font-size: 11px;
            font-weight: 500;
        }}

        .card-actions-row {{
            display: grid;
            grid-template-columns: 1fr auto auto;
            gap: 6px;
            align-items: center;
        }}

        .btn-wa-card {{
            text-align: center;
            padding: 8px 10px;
            background: var(--donalu-whatsapp);
            color: #ffffff;
            border-radius: var(--radius-sm);
            font-size: 11.5px;
            font-weight: 700;
            text-decoration: none;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
        }}

        .btn-wa-card:hover {{
            background: var(--donalu-whatsapp-dark);
        }}

        .btn-site-card {{
            padding: 8px 10px;
            background: #eff6ff;
            color: var(--donalu-blue-primary);
            border: 1px solid #bfdbfe;
            border-radius: var(--radius-sm);
            font-size: 11.5px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.2s;
            white-space: nowrap;
        }}

        .btn-site-card:hover {{
            background: var(--donalu-blue-primary);
            color: #ffffff;
        }}

        .btn-comment-card {{
            background: #f1f5f9;
            border: 1px solid var(--donalu-border);
            color: #475569;
            padding: 8px 10px;
            border-radius: var(--radius-sm);
            font-size: 11.5px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
        }}

        .btn-comment-card:hover {{
            background: #e2e8f0;
            color: #0f172a;
        }}

        /* === 4. CONTRA-CAPA (DONA LU BACK COVER) === */
        .donalu-back-cover {{
            min-height: 90vh;
            background: radial-gradient(circle at 20% 80%, #002266 0%, #001f56 50%, #001233 100%);
            border-radius: var(--radius-xl);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 60px;
            color: #ffffff;
            box-shadow: 0 25px 60px -15px rgba(0, 20, 56, 0.45);
            margin-top: 60px;
            page-break-before: always;
            break-before: page;
            border: 2px solid rgba(253, 184, 39, 0.3);
        }}

        .back-cover-head {{
            text-align: center;
            max-width: 800px;
            margin: 0 auto;
            position: relative;
            z-index: 2;
        }}

        .back-cover-logo-img {{
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: #ffffff;
            padding: 4px;
            box-shadow: 0 0 0 4px var(--donalu-yellow);
            margin-bottom: 16px;
        }}

        .back-cover-heading {{
            font-family: var(--font-display);
            font-size: 36px;
            font-weight: 800;
            letter-spacing: -0.5px;
            color: #ffffff;
        }}

        .back-cover-sub {{
            font-size: 15px;
            color: var(--donalu-yellow);
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-top: 4px;
        }}

        .back-cover-content-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 30px;
            position: relative;
            z-index: 2;
            margin: 40px 0;
        }}

        .donalu-contact-panel {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: var(--radius-lg);
            padding: 30px;
            backdrop-filter: blur(10px);
            border-left: 5px solid var(--donalu-yellow);
        }}

        .panel-title {{
            font-family: var(--font-display);
            font-size: 20px;
            font-weight: 700;
            color: var(--donalu-yellow);
            margin-bottom: 18px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .contact-detail-row {{
            margin-bottom: 14px;
        }}

        .contact-detail-label {{
            font-size: 11px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 2px;
        }}

        .contact-detail-val {{
            font-size: 15px;
            color: #ffffff;
            font-weight: 600;
        }}

        .contact-detail-val a {{
            color: #ffffff;
            text-decoration: none;
            transition: color 0.2s;
        }}

        .contact-detail-val a:hover {{
            color: var(--donalu-yellow);
        }}

        .donalu-pillars-panel {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: var(--radius-lg);
            padding: 30px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .pillars-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 14px;
            font-size: 13.5px;
            color: #cbd5e1;
        }}

        .pillars-list li {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
            line-height: 1.5;
        }}

        .pillar-check {{
            color: var(--donalu-yellow);
            font-weight: 800;
            font-size: 15px;
        }}

        .back-cover-bottom {{
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
            background: rgba(0, 20, 56, 0.65);
            backdrop-filter: blur(5px);
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
            padding: 28px;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.3);
            position: relative;
            border-top: 5px solid var(--donalu-yellow);
        }}

        .modal-title {{
            font-family: var(--font-display);
            font-size: 19px;
            font-weight: 800;
            color: var(--donalu-navy);
            margin-bottom: 4px;
        }}

        .modal-subtitle {{
            font-size: 13px;
            color: var(--donalu-text-muted);
            margin-bottom: 18px;
        }}

        .modal-textarea {{
            width: 100%;
            height: 120px;
            border: 1px solid var(--donalu-border);
            border-radius: var(--radius-md);
            padding: 12px;
            font-family: var(--font-body);
            font-size: 14px;
            outline: none;
            resize: vertical;
            margin-bottom: 16px;
        }}

        .modal-textarea:focus {{
            border-color: var(--donalu-blue-primary);
            box-shadow: 0 0 0 3px rgba(0, 60, 165, 0.15);
        }}

        .modal-status-select {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }}

        .status-radio-label {{
            flex: 1;
            padding: 9px 12px;
            border: 1px solid var(--donalu-border);
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
            border-color: var(--donalu-blue-primary);
            background: var(--donalu-blue-light);
            color: var(--donalu-blue-primary);
        }}

        .modal-actions {{
            display: flex;
            justify-content: flex-end;
            gap: 10px;
        }}

        /* === DRAWER LATERAL DE FEEDBACKS === */
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
            width: 450px;
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
            padding: 22px;
            background: var(--donalu-navy);
            color: #ffffff;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid var(--donalu-yellow);
        }}

        .drawer-header h3 {{
            font-family: var(--font-display);
            font-size: 18px;
            font-weight: 800;
            color: #ffffff;
        }}

        .drawer-close-btn {{
            background: transparent;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: var(--donalu-yellow);
        }}

        .drawer-body {{
            padding: 20px;
            overflow-y: auto;
            flex: 1;
        }}

        .drawer-footer {{
            padding: 16px 20px;
            border-top: 1px solid var(--donalu-border);
            display: flex;
            gap: 10px;
            background: #f8fafc;
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
                font-size: 10.5pt;
            }}

            .donalu-topbar,
            .filter-ribbon,
            .btn-comment-card,
            .btn-wa-card,
            .feedback-mark-btn,
            .modal-overlay,
            .drawer-overlay,
            .feedback-drawer,
            .btn-site-card {{
                display: none !important;
            }}

            .catalog-viewport {{
                max-width: 100% !important;
                padding: 0 !important;
                margin: 0 !important;
            }}

            .donalu-cover {{
                min-height: 275mm !important;
                border-radius: 0 !important;
                box-shadow: none !important;
                page-break-after: always !important;
                break-after: page !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }}

            .donalu-about-toc {{
                border-radius: 0 !important;
                box-shadow: none !important;
                border: 1px solid #ccc !important;
                page-break-after: always !important;
                break-after: page !important;
            }}

            .catalog-segment-block {{
                page-break-before: always !important;
                break-before: page !important;
            }}

            .products-grid-layout {{
                grid-template-columns: repeat(2, 1fr) !important;
                gap: 12mm !important;
            }}

            .product-card {{
                box-shadow: none !important;
                border: 1px solid #cbd5e1 !important;
                break-inside: avoid !important;
                page-break-inside: avoid !important;
            }}

            .donalu-back-cover {{
                min-height: 275mm !important;
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

        @media (max-width: 768px) {{
            .cover-hero-headline {{
                font-size: 36px;
            }}
            .donalu-cover, .donalu-back-cover {{
                padding: 30px 20px;
            }}
            .about-grid-lead {{
                grid-template-columns: 1fr;
            }}
            .products-grid-layout {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>

    <!-- DONA LU BRANDED TOPBAR -->
    <header class="donalu-topbar">
        <div class="topbar-container">
            <a href="#" class="brand-identity">
                <img src="assets_donalu/logo-donalu-128.png" alt="Dona Lu Logo" class="brand-logo-img">
                <div class="brand-text-block">
                    <span class="brand-name">DONA LU <span class="brand-name-accent">· LIMPEZA</span></span>
                    <span class="brand-subtext">Distribuidora Autorizada Start Química</span>
                </div>
            </a>

            <div class="topbar-search-wrap">
                <span class="search-lens-icon">🔍</span>
                <input type="text" id="liveSearch" class="topbar-search-input" placeholder="Buscar produto, ativo, fragrância ou embalagem..." oninput="handleSearch()">
            </div>

            <div class="topbar-actions">
                <a href="https://wa.me/5517981321919" target="_blank" class="btn-topbar btn-topbar-whatsapp" title="WhatsApp Dona Lu">
                    <span>💬</span> (17) 98132-1919
                </a>
                <button class="btn-topbar btn-topbar-print" onclick="window.print()">
                    <span>🖨️</span> Salvar em PDF (A4)
                </button>
                <button class="btn-topbar btn-topbar-feedback" onclick="toggleDrawer()">
                    <span>📝</span> Palpites (<span id="feedbackCounter">0</span>)
                </button>
            </div>
        </div>
    </header>

    <!-- FILTER BAR -->
    <div class="filter-ribbon">
        <div class="filter-ribbon-inner">
            <button class="filter-btn active" onclick="filterSegment('all', this)">
                Todos os Produtos <span class="btn-counter">80</span>
            </button>
            <button class="filter-btn" onclick="filterSegment('Pisos, Pedras e Tratamento de Superfícies', this)">
                🏛️ Pisos & Pedras <span class="btn-counter">{len(by_segment.get('Pisos, Pedras e Tratamento de Superfícies', []))}</span>
            </button>
            <button class="filter-btn" onclick="filterSegment('Desinfecção e Limpeza Geral Multiuso', this)">
                ✨ Desinfecção & Limpeza <span class="btn-counter">{len(by_segment.get('Desinfecção e Limpeza Geral Multiuso', []))}</span>
            </button>
            <button class="filter-btn" onclick="filterSegment('Lavanderia e Tratamento de Roupas', this)">
                🧺 Lavanderia <span class="btn-counter">{len(by_segment.get('Lavanderia e Tratamento de Roupas', []))}</span>
            </button>
            <button class="filter-btn" onclick="filterSegment('Cozinha e Tratamento de Metais', this)">
                🍳 Cozinha & Metais <span class="btn-counter">{len(by_segment.get('Cozinha e Tratamento de Metais', []))}</span>
            </button>
            <button class="filter-btn" onclick="filterSegment('Higiene Pessoal e Antissepsia', this)">
                🧴 Asseptgel & Higiene <span class="btn-counter">{len(by_segment.get('Higiene Pessoal e Antissepsia', []))}</span>
            </button>
            <button class="filter-btn" onclick="filterSegment('Aromatização e Cuidados Pet', this)">
                🌸 Aromatizantes & Pet <span class="btn-counter">{len(by_segment.get('Aromatização e Cuidados Pet', []))}</span>
            </button>
            <button class="filter-btn" onclick="filterSegment('Automotivo e Oficinas', this)">
                🚗 Linha Automotiva <span class="btn-counter">{len(by_segment.get('Automotivo e Oficinas', []))}</span>
            </button>
        </div>
    </div>

    <main class="catalog-viewport">

        <!-- 1. CAPA DO CATÁLOGO (DONA LU FRONT COVER) -->
        <div class="donalu-cover">
            <div class="cover-accent-halo"></div>
            <div class="cover-golden-stripe"></div>

            <div class="cover-top-header">
                <div class="cover-brand-showcase">
                    <img src="assets_donalu/logo-donalu-256.png" alt="Dona Lu Logo Oficial" class="cover-main-logo">
                    <div class="cover-title-lockup">
                        <div class="cover-company-name">DONA LU <span>MATERIAIS</span></div>
                        <div class="cover-company-tag">Produtos de Limpeza Profissional · São José do Rio Preto</div>
                    </div>
                </div>
                <div class="cover-badge-edition">
                    EDIÇÃO 2026 / 2027
                </div>
            </div>

            <div class="cover-center-editorial">
                <div class="cover-label-pill">🌟 Portfólio Comercial Homologado</div>
                <h1 class="cover-hero-headline">
                    Catálogo Oficial de <span class="highlight">Produtos de Limpeza Profissional</span>
                </h1>
                <p class="cover-hero-lead">
                    Apresentação completa das soluções químicas de alta performance distribuídas pela <strong>Dona Lu</strong> em parceria oficial com a <strong>Start Química</strong>. Fórmulas de padrão industrial para empresas, condomínios, indústrias, lavanderias e pós-obra.
                </p>

                <div class="cover-metrics-grid">
                    <div class="cover-metric-card">
                        <div class="metric-big">80+</div>
                        <div class="metric-caption">Produtos em Estoque</div>
                    </div>
                    <div class="cover-metric-card">
                        <div class="metric-big">7</div>
                        <div class="metric-caption">Linhas Especializadas</div>
                    </div>
                    <div class="cover-metric-card">
                        <div class="metric-big">100%</div>
                        <div class="metric-caption">Homologado Anvisa</div>
                    </div>
                    <div class="cover-metric-card">
                        <div class="metric-big">START</div>
                        <div class="metric-caption">Parceria Autorizada</div>
                    </div>
                </div>
            </div>

            <div class="cover-bottom-bar">
                <div class="cover-distrib-info">
                    Distribuição & Consultoria Técnica: <strong>Dona Lu Materiais de Limpeza</strong><br>
                    Atendimento Especializado: São José do Rio Preto e Região &bull; WhatsApp: (17) 98132-1919
                </div>
                <div class="cover-seals-flex">
                    <span class="cover-seal-pill">Linhas Azulim &bull; Tuff &bull; Pedrex &bull; Asseptgel</span>
                    <span class="cover-seal-pill">Pós-Obra &bull; Empresas &bull; Condomínios</span>
                </div>
            </div>
        </div>

        <!-- 2. APRESENTAÇÃO DONA LU & ÍNDICE GERAL -->
        <section class="donalu-about-toc">
            <div class="about-grid-lead">
                <div class="about-lead-text">
                    <h2>Soluções Profissionais que Fazem a Diferença</h2>
                    <p>
                        A <strong>Dona Lu</strong> é a sua distribuidora especializada em produtos de limpeza profissional em São José do Rio Preto e região. Oferecemos assessoria técnica completa para redução de custos com diluição inteligente, consultoria para limpeza pesada e pós-obra, além de atendimento sob medida para empresas, condomínios e residências.
                    </p>
                    <p>
                        Em parceria direta com a <strong>Start Química</strong>, garantimos acesso a marcas líderes como <em>Azulim, Tuff, Pedrex, Asseptgel, Alumil e Indy Cryl</em>, unindo poder desincrustante, rentabilidade e responsabilidade ambiental.
                    </p>
                </div>

                <div class="about-contact-quickbox">
                    <div class="quickbox-item">
                        <div class="quickbox-label">Central de Atendimento & Orçamentos:</div>
                        <div class="quickbox-val"><a href="https://wa.me/5517981321919" target="_blank" style="color:var(--donalu-blue-primary); text-decoration:none;">📲 (17) 98132-1919 (WhatsApp)</a></div>
                    </div>
                    <div class="quickbox-item">
                        <div class="quickbox-label">E-mail Comercial:</div>
                        <div class="quickbox-val">donalumateriais@gmail.com</div>
                    </div>
                    <div class="quickbox-item">
                        <div class="quickbox-label">Localização & Entregas:</div>
                        <div class="quickbox-val">São José do Rio Preto, SP</div>
                    </div>
                    <div class="quickbox-item">
                        <div class="quickbox-label">Instagram Oficial:</div>
                        <div class="quickbox-val"><a href="https://www.instagram.com/donalumateriaisdelimpeza/" target="_blank" style="color:var(--donalu-blue-primary); text-decoration:none;">@donalumateriaisdelimpeza</a></div>
                    </div>
                </div>
            </div>

            <div class="toc-title-row">
                <h3>Sumário de Linhas e Segmentos</h3>
            </div>
            <div class="toc-tiles-grid">
                {''.join(toc_items)}
            </div>
        </section>

        <!-- 3. MIOLO COM OS SEGMENTOS E OS 80 PRODUTOS -->
        {''.join(segments_html)}

        <!-- 4. CONTRA-CAPA (DONA LU BACK COVER) -->
        <div class="donalu-back-cover">
            <div class="cover-golden-stripe"></div>

            <div class="back-cover-head">
                <img src="assets_donalu/logo-donalu-256.png" alt="Dona Lu Logo" class="back-cover-logo-img">
                <div class="back-cover-heading">DONA LU MATERIAIS DE LIMPEZA</div>
                <div class="back-cover-sub">Eficiência, Qualidade e Economia Comprovada</div>
            </div>

            <div class="back-cover-content-grid">
                <div class="donalu-contact-panel">
                    <div class="panel-title">📞 Contato & Pedidos</div>
                    
                    <div class="contact-detail-row">
                        <div class="contact-detail-label">Razão Social:</div>
                        <div class="contact-detail-val">Dona Lu Materiais de Limpeza</div>
                    </div>

                    <div class="contact-detail-row">
                        <div class="contact-detail-label">CNPJ:</div>
                        <div class="contact-detail-val">69.236.751/0001-08</div>
                    </div>

                    <div class="contact-detail-row">
                        <div class="contact-detail-label">WhatsApp Comercial:</div>
                        <div class="contact-detail-val"><a href="https://wa.me/5517981321919" target="_blank">(17) 98132-1919</a></div>
                    </div>

                    <div class="contact-detail-row">
                        <div class="contact-detail-label">E-mail:</div>
                        <div class="contact-detail-val">donalumateriais@gmail.com</div>
                    </div>

                    <div class="contact-detail-row">
                        <div class="contact-detail-label">Horário de Atendimento:</div>
                        <div class="contact-detail-val">Segunda a Sexta: 8h às 18h | Sábado: 8h às 12h</div>
                    </div>

                    <div class="contact-detail-row">
                        <div class="contact-detail-label">Endereço & Atendimento:</div>
                        <div class="contact-detail-val">São José do Rio Preto - SP (Atendimento Regional)</div>
                    </div>
                </div>

                <div class="donalu-pillars-panel">
                    <div class="panel-title" style="color:#ffffff;">Diferenciais Dona Lu</div>
                    <ul class="pillars-list">
                        <li><span class="pillar-check">✓</span> <strong>Consultoria Técnica Gratuita:</strong> Orientamos a diluição correta para reduzir em até 40% o custo por metro quadrado limpo.</li>
                        <li><span class="pillar-check">✓</span> <strong>Especialistas em Pós-Obra:</strong> Produtos de ação desincrustante comprovada para pisos finos, pedras e vidros.</li>
                        <li><span class="pillar-check">✓</span> <strong>Parceria Oficial Start Química:</strong> Garantia de procedência com laudos técnicos e registro Anvisa.</li>
                        <li><span class="pillar-check">✓</span> <strong>Pronta Entrega e Atendimento Ágil:</strong> Fornecimento contínuo para condomínios, clínicas, escolas e indústrias.</li>
                        <li><span class="pillar-check">✓</span> <strong>Locação de Máquinas:</strong> Soluções completas com enceradeiras, lavadoras e aspiradores profissionais.</li>
                    </ul>
                </div>
            </div>

            <div class="back-cover-bottom">
                <p>&copy; 2026 Dona Lu Materiais de Limpeza · CNPJ 69.236.751/0001-08 · Distribuidora Autorizada Start Química.<br>
                Catálogo comercial formatado para apresentação digital e impressão técnica A4.</p>
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
                <button class="btn-topbar btn-topbar-print" onclick="saveProductComment()">Salvar Palpite</button>
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
            <p style="color: #64748b; font-size: 14px;">Nenhum palpite registrado ainda. Clique no botão "💬 Palpite" em qualquer produto ou marque as bolinhas para aprovar/ajustar.</p>
        </div>
        <div class="drawer-footer">
            <button class="btn-topbar btn-topbar-print" style="flex:1;" onclick="copyFeedbackToClipboard()">📋 Copiar Resumo dos Palpites</button>
            <button class="btn-topbar" style="background:#f1f5f9; color:#475569;" onclick="clearAllFeedbacks()">Limpar</button>
        </div>
    </div>

    <script>
        let feedbackData = JSON.parse(localStorage.getItem('donalu_catalog_feedbacks') || '{{}}');
        let currentModalProductId = null;

        function updateFeedbackUI() {{
            const keys = Object.keys(feedbackData);
            document.getElementById('feedbackCounter').innerText = keys.length;

            document.querySelectorAll('.product-card').forEach(card => {{
                card.classList.remove('card-approved', 'card-needs-adjust');
                const btn = card.querySelector('.feedback-mark-btn');
                if (btn) btn.innerText = '⚪';
            }});

            const drawerList = document.getElementById('drawerList');
            if (keys.length === 0) {{
                drawerList.innerHTML = '<p style="color: #64748b; font-size: 14px; text-align:center; padding: 30px 10px;">Nenhum palpite ou anotação registrada ainda.<br><br>💡 Você ou a pessoa que está revisando podem clicar em <strong>"💬 Palpite"</strong> nos produtos para sugerir mudanças de texto, foto ou embalagem.</p>';
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
            localStorage.setItem('donalu_catalog_feedbacks', JSON.stringify(feedbackData));
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

        // Search Filter
        function handleSearch() {{
            const q = document.getElementById('liveSearch').value.toLowerCase().trim();
            const cards = document.querySelectorAll('.product-card');
            cards.forEach(card => {{
                const name = card.getAttribute('data-name');
                const active = card.getAttribute('data-active');
                const frag = card.getAttribute('data-fragrance');
                const brand = card.getAttribute('data-brand');
                const text = card.innerText.toLowerCase();
                if (!q || name.includes(q) || active.includes(q) || frag.includes(q) || brand.includes(q) || text.includes(q)) {{
                    card.style.display = 'flex';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}

        // Segment Filter
        function filterSegment(seg, btn) {{
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const sections = document.querySelectorAll('.catalog-segment-block');
            if (seg === 'all') {{
                sections.forEach(s => s.style.display = 'block');
            }} else {{
                sections.forEach(s => {{
                    const header = s.querySelector('.seg-banner-title').innerText;
                    if (header.includes(seg) || seg.includes(header)) {{
                        s.style.display = 'block';
                    }} else {{
                        s.style.display = 'none';
                    }}
                }});
            }}
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
    f.write(html_output)

print("Novo catálogo da Dona Lu gerado com sucesso em catalogo_visual.html!")

