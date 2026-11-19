import json
import os
import re
import urllib.parse

# Load enriched product data
with open('catalogo_detalhado.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

# Thematic segment order
segment_order = [
    "Pisos, Pedras e Tratamento de Superfícies",
    "Desinfecção e Limpeza Geral Multiuso",
    "Lavanderia e Tratamento de Roupas",
    "Cozinha e Tratamento de Metais",
    "Higiene Pessoal e Antissepsia",
    "Aromatização e Cuidados Pet",
    "Automotivo e Oficinas"
]

# Segment display mappings matching example style
SEGMENT_BADGES = {
    "Pisos, Pedras e Tratamento de Superfícies": "PISOS & PEDRAS",
    "Desinfecção e Limpeza Geral Multiuso": "DESINFECÇÃO & MULTIUSO",
    "Lavanderia e Tratamento de Roupas": "LAVANDERIA & TECIDOS",
    "Cozinha e Tratamento de Metais": "COZINHA & LOUÇAS",
    "Higiene Pessoal e Antissepsia": "HIGIENE & ASSEPTGEL",
    "Aromatização e Cuidados Pet": "AROMATIZANTES & PET",
    "Automotivo e Oficinas": "AUTOMOTIVA"
}

# Concise, objective, practical directions function
def summarize_direction(name, raw, segment):
    name_l = name.lower()
    if "limpa pedras" in name_l:
        return "Remoção pesada de sujidades e incrustações em pedras e pisos rústicos. Diluição de 1:3 a 1:5."
    elif "sabão de querosene" in name_l or "sabao de querosene" in name_l:
        return "Detergente desengordurante e desengraxante multiuso de alta performance para pisos e graxas."
    elif "cera líquida pretita" in name_l or "pretita" in name_l:
        return "Cera líquida especial para brilho e renovação de pneus, tapetes de borracha, pisos e couro."
    elif "percarbonato" in name_l:
        return "Alvejante com oxigênio ativo puro para remoção profunda de manchas difíceis em roupas e superfícies."
    elif "tira limo" in name_l:
        return "Ação rápida contra limo, mofo e fungos em azulejos, rejuntes, ralos e boxes de banheiro."
    elif "alvejante sem cloro" in name_l:
        return "Tira-manchas com oxigênio ativo seguro para roupas brancas e coloridas, sem desbotar."
    elif "tira ferrugem" in name_l:
        return "Aplicação direta em manchas de ferrugem em tecidos e pisos. Ação desincrustante localizada."
    elif "flotador" in name_l:
        return "Limpeza instantânea por flotação de partículas em estofados, fórmicas, plásticos, vinil e pisos."
    elif "cera acrílica" in name_l or "cera auto brilho" in name_l:
        return "Impermeabilização e película protetora com brilho espelhado antiderrapante de longa durabilidade."
    elif "lava roupas" in name_l:
        return "Lavagem profunda com alto poder de remoção de sujeiras, perfume duradouro e cuidado com os fios."
    elif "laminados" in name_l:
        return "Limpeza e proteção especializada para pisos laminados e vinílicos, sem agredir o acabamento."
    elif "brilha inox" in name_l:
        return "Limpa, protege e dá brilho espelhado em superfícies de inox, sem riscar e repelindo poeira."
    elif "limpador gel" in name_l:
        return "Limpador concentrado de alto rendimento para pisos e azulejos, com agradável aroma duradouro."
    elif "limpa telas" in name_l:
        return "Fórmula suave antiestática para remoção de poeira e marcas de dedos em telas, TVs e monitores."
    elif "água sanitária" in name_l:
        return "Desinfecção bactericida geral de ambientes, banheiros e alvejamento eficiente de roupas brancas."
    elif "tuff sem passar" in name_l:
        return "Desamassa tecidos a seco instantaneamente com aroma suave, dispensando o uso do ferro."
    elif "querosene azulim" in name_l:
        return "Solvente multiuso para remoção de tintas frescas, graxas, colas e desengraxe mecânico geral."
    elif "desengordurante" in name_l:
        return "Dissolução rápida de gorduras pesadas em fogões, coifas, bancadas, grelhas e azulejos."
    elif "sabonete" in name_l:
        return "Higienização e antissepsia suave das mãos para uso profissional, hospitalar e doméstico."
    elif "clorogel" in name_l or "cloro ativo" in name_l:
        return "Poder desinfetante com cloro ativo que adere às superfícies verticais, eliminando bactérias."
    elif "limpa vidros" in name_l:
        return "Fórmula desengordurante de secagem ultra rápida que limpa vidros e espelhos sem manchas."
    elif "pasta de brilho" in name_l or "alumil" in name_l:
        return "Polimento e brilho espelhado em panelas, formas, torneiras e utensílios de alumínio e metais."
    elif "lava louças" in name_l:
        return "Remoção de gorduras difíceis em louças, panelas e talheres com alto rendimento e pH neutro."
    elif "óleo silicone" in name_l or "silicone" in name_l:
        return "Proteção e renovação de painéis plásticos, borrachas e frisos, evitando ressecamento."
    elif "amaciante" in name_l:
        return "Maciez extrema às fibras do tecido com microcápsulas de perfume com liberação prolongada."
    elif "neutralizador de odores" in name_l or "free pet" in name_l:
        return "Eliminação biológica de odores desagradáveis de ambientes fechados, urina e animais de estimação."
    elif "maximoom" in name_l:
        return "Detergente desinfetante concentrado de alta diluição para limpeza predial e industrial pesada."
    elif "rejuntes" in name_l:
        return "Desincrustação profunda de sujidades e bolor em rejuntes encardidos de pisos e paredes."
    elif "couro" in name_l:
        return "Limpeza, hidratação profunda e restauração da flexibilidade de estofados e artigos de couro."
    elif "clorexidina" in name_l:
        return "Antissepsia preventiva tópica da pele com ação residual antimicrobiana prolongada."
    elif "air fryer" in name_l or "fornos" in name_l:
        return "Desincrustante específico para quebrar gordura carbonizada em air fryers, fornos e micro-ondas."
    elif "pedra sanitária" in name_l:
        return "Higienização contínua e perfumação duradoura a cada descarga em vasos sanitários."
    elif "naftalina" in name_l:
        return "Proteção preventiva e repelente contra traças, insetos e odores em armários e gavetas."
    elif "grelhas" in name_l:
        return "Ação desincrustante rápida contra gorduras carbonizadas e restos de carne em churrasqueiras."
    elif "amoniacal" in name_l:
        return "Detergente de forte ação saponificante para remoção de ceras antigas e óleos industriais."
    elif "difusor" in name_l:
        return "Aromatização contínua e sofisticada de ambientes por varetas condutoras de fragrância fina."
    elif "soda" in name_l:
        return "Desentupimento de pias e ralos e desincrustação extrema de gorduras pesadas industriais."
    elif "automotiva" in name_l or "brilha pneu" in name_l:
        return "Acabamento profissional de alto brilho e proteção com efeito molhado para pneus e latarias."
    elif "cerâmicas" in name_l or "porcelanato" in name_l:
        return "Limpeza diária e manutenção de porcelanatos e pisos nobres, sem embaçar nem agredir o brilho."
    elif "lustra móveis" in name_l:
        return "Limpeza, brilho e camada protetora contra poeira e umidade em móveis de madeira."
    elif "saponáceo" in name_l:
        return "Limpeza profunda sem riscar louças sanitárias, azulejos e superfícies esmaltadas."
    elif "passa fácil" in name_l:
        return "Facilita o deslizamento do ferro, alinhando as fibras e deixando as roupas cheirosas."
    elif "álcool" in name_l and ("gel" in name_l or "46" in name_l or "70" in name_l):
        return "Higienização e desinfecção imediata com rápida secagem e proteção comprovada contra bactérias."
    elif "bloqueador" in name_l:
        return "Barreira aromática preventiva sobre a água do vaso sanitário que impede a liberação de odores."
    elif "espuma" in name_l:
        return "Espuma ativa de limpeza a seco para sofás, carpetes, estofados automotivos e tênis."
    else:
        if raw and len(raw) > 15:
            first = raw.split('.')[0] + '.'
            if len(first) < 110:
                return first
        return f"Produto de alta performance da linha {segment}, para limpeza, higienização e manutenção."

products_sorted = sorted(products, key=lambda p: (
    segment_order.index(p['segment']) if p['segment'] in segment_order else 99,
    p['index']
))

# Group products into EXACTLY 2 PRODUCTS PER A4 PAGE
pages = []
for i in range(0, len(products_sorted), 2):
    pages.append(products_sorted[i:i+2])

total_product_pages = len(pages) # 40 pages

def render_example_card(p):
    safe_png = f"imagens_produtos/{p['png_file'].replace('%', '%25')}"
    badge_text = SEGMENT_BADGES.get(p['segment'], "LIMPEZA GERAL")
    
    # Packaging formatting
    pkgs = [x.strip() for x in p['packaging'].split(',') if x.strip()]
    if pkgs:
        primary_vol = pkgs[0]
        other_vols = " e ".join(pkgs[1:]) if len(pkgs) > 1 else ""
        vol_str = f"<strong>{primary_vol}</strong>" + (f" e {other_vols}" if other_vols else "") + " — Embalagem oficial"
    else:
        vol_str = "<strong>Sob consulta</strong> — Frasco / Bombona"
        
    # Summarized direct usage indication
    directions_summary = summarize_direction(p['name'], p['directions'], p['segment'])
    
    # WhatsApp request message
    wa_msg = urllib.parse.quote(f"Olá Dona Lu! Tenho interesse no produto: {p['name']} (Item #{p['index']:03d}). Poderia me passar um orçamento?")
    
    return f"""
    <div class="product-item-card" data-id="{p['index']}">
        <!-- LEFT: VISUAL STAGE WITH BUBBLES & HIGH-RES PACKSHOT (EAGER LOADING) -->
        <div class="card-visual-col">
            <div class="bubble bubble-1"></div>
            <div class="bubble bubble-2"></div>
            <div class="bubble bubble-3"></div>
            <img src="{safe_png}" alt="{p['name']}" loading="eager" class="product-packshot-img" onerror="this.onerror=null; this.src='{safe_png.replace('%25', '%')}';">
            <span class="product-brand-caption">{p['brand']}</span>
        </div>

        <!-- RIGHT: TECHNICAL DETAILS COMPACT & CONTIGUOUS (NO GAP BETWEEN BADGE AND IDENTIFICAÇÃO) -->
        <div class="card-info-col">
            <div class="card-title-header">
                <h3 class="prod-title">{p['name']}</h3>
                <div class="prod-badge-pill">{badge_text}</div>
            </div>

            <div class="meta-section">
                <div class="meta-row">
                    <span class="meta-lbl">IDENTIFICAÇÃO</span>
                    <span class="meta-txt">Cód. #{p['index']:03d} | Marca: <strong>{p['brand']}</strong></span>
                </div>

                <div class="meta-row">
                    <span class="meta-lbl">VOLUME E EMBALAGEM</span>
                    <span class="meta-txt pkg-highlight">{vol_str}</span>
                </div>

                <div class="meta-row">
                    <span class="meta-lbl">INDICAÇÃO DE USO</span>
                    <span class="meta-txt directions-text">{directions_summary}</span>
                </div>

                <div class="meta-row">
                    <span class="meta-lbl">FRAGRÂNCIA</span>
                    <span class="meta-txt">{p['fragrance']}</span>
                </div>

                <div class="meta-row">
                    <span class="meta-lbl">ATIVOS</span>
                    <span class="meta-txt active-highlight">{p['active']}</span>
                </div>
            </div>

            <div class="card-btn-strip">
                <a href="https://wa.me/5517981321919?text={wa_msg}" target="_blank" class="btn-wa-compact" title="Pedir no WhatsApp">
                    <span>Pedir no WhatsApp</span>
                </a>
                <a href="{p['product_url']}" target="_blank" class="btn-site-compact" title="Ver no site Start Química">
                    Ficha Técnica
                </a>
                <button class="btn-feedback-compact" onclick="openCommentModal({p['index']})" title="Deixar observação">
                    💬 Palpite
                </button>
            </div>
        </div>
    </div>
    """

# Build each A4 product sheet (pages 3 to 42)
product_sheets_html = []
for p_idx, pair in enumerate(pages, start=3):
    cards_html = "\n".join([render_example_card(p) for p in pair])
    
    # Identify segment for this specific page header
    main_seg = pair[0]['segment']
    header_seg_name = SEGMENT_BADGES.get(main_seg, "PRODUTOS PROFISSIONAIS")
    
    sheet_html = f"""
    <!-- PÁGINA {p_idx} DO CATÁLOGO (A4) -->
    <div class="a4-sheet product-sheet" data-page="{p_idx}">
        <!-- PROMINENT BLUE TOP HEADER BAR WITH DYNAMIC SEGMENT NAME -->
        <header class="sheet-top-bar">
            <div class="header-brand-side">
                <img src="assets_donalu/dona-lu-avatar-smooth.png" alt="Dona Lu Logo" class="header-logo-icon">
                <div class="header-brand-text-block">
                    <span class="header-brand-text">DONA LU MATERIAIS</span>
                    <span class="header-brand-sub">Limpeza Profissional · Distribuidora Start Química</span>
                </div>
            </div>
            <div class="header-section-side">
                <span class="header-seg-label">LINHA {header_seg_name}</span>
            </div>
        </header>

        <!-- TWO VERTICALLY STACKED CARDS -->
        <div class="sheet-cards-stack">
            {cards_html}
        </div>

        <!-- RUNNING FOOTER -->
        <footer class="sheet-footer-bar">
            <div class="footer-left-note">
                Catálogo de Produtos de Limpeza 2026 | Dona Lu Materiais · WhatsApp: (17) 98132-1919
            </div>
            <div class="footer-page-num">
                {p_idx}
            </div>
        </footer>
    </div>
    """
    product_sheets_html.append(sheet_html)

# Build Table of Contents list for Page 2
toc_rows_html = []
for seg in segment_order:
    seg_badge = SEGMENT_BADGES.get(seg, "GERAL")
    seg_items = [p for p in products_sorted if p['segment'] == seg]
    if not seg_items:
        continue
    start_p = 3
    for p_idx, pair in enumerate(pages, start=3):
        if any(p['segment'] == seg for p in pair):
            start_p = p_idx
            break
            
    sample_names = ", ".join([p['name'].split()[0] + " " + " ".join(p['name'].split()[1:3]) for p in seg_items[:3]])
    
    toc_rows_html.append(f"""
        <div class="toc-table-row">
            <div class="toc-col-title">
                <strong>LINHA {seg_badge}</strong> — {sample_names}...
            </div>
            <div class="toc-col-cat">
                {len(seg_items)} produtos
            </div>
            <div class="toc-col-page">
                {start_p}
            </div>
        </div>
    """)

# Select 3 featured packshots for the front cover center
featured_packshots = [
    f"imagens_produtos/{products_sorted[0]['png_file'].replace('%', '%25')}",
    f"imagens_produtos/{products_sorted[5]['png_file'].replace('%', '%25')}",
    f"imagens_produtos/{products_sorted[12]['png_file'].replace('%', '%25')}",
]

# Generate Full Master HTML matching the Example PDF with NO GAP between badge and identificação
full_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo de Produtos de Limpeza 2026 — Dona Lu Materiais</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Montserrat:wght@500;600;700;800&display=swap" rel="stylesheet">
    <link rel="icon" type="image/png" href="assets_donalu/logo-donalu-128.png">

    <style>
        /* === COLOR TOKENS EXACTLY MATCHING THE USER EXAMPLE PDF & DONA LU BRAND === */
        :root {{
            --pdf-blue-cover:     #0D4884; /* Deep rich blue from cover page */
            --pdf-blue-bar:       #0A4275; /* Header blue bar */
            --pdf-blue-title:     #073562; /* Main headings blue */
            --pdf-blue-pill:      #007ACC; /* Solid bright blue pill */
            --pdf-blue-label:     #005A94; /* Metadata labels */
            --pdf-card-bg:        #EEF6FB; /* Soft light blue/ice tint of cards */
            --pdf-bubble-1:       #E2EFF8; /* Soft circle 1 */
            --pdf-bubble-2:       #D8E8F5; /* Soft circle 2 */
            --pdf-yellow-line:    #FDB827; /* Dona Lu Yellow accent */
            --pdf-yellow-dark:    #E9A30F;
            --pdf-text-dark:      #111827; /* High contrast body text for phone reading */
            --pdf-text-muted:     #4B5563;
            --pdf-border-line:    #E2E8F0;
            --donalu-whatsapp:    #25D366;
            
            --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            --font-display: 'Plus Jakarta Sans', sans-serif;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-font-smoothing: antialiased;
        }}

        body {{
            background-color: #4A4D50; /* Adobe Acrobat / Canva dark desktop backdrop */
            font-family: var(--font-sans);
            color: var(--pdf-text-dark);
            line-height: 1.45;
            padding-bottom: 80px;
        }}

        /* === TOP SCREEN CONTROLS (HIDDEN ON PRINT) === */
        .screen-topbar {{
            position: sticky;
            top: 0;
            z-index: 1000;
            background: #0A3660;
            border-bottom: 3px solid var(--pdf-yellow-line);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            padding: 10px 24px;
            color: #ffffff;
        }}

        .topbar-wrapper {{
            max-width: 1300px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
        }}

        .brand-link {{
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
            color: #ffffff;
        }}

        .brand-logo-circle {{
            height: 44px;
            width: 44px;
            border-radius: 50%;
            background: #ffffff;
            padding: 2px;
            box-shadow: 0 0 0 2.5px var(--pdf-yellow-line);
        }}

        .brand-text-name {{
            font-size: 19px;
            font-weight: 800;
            letter-spacing: -0.5px;
        }}

        .brand-text-name span {{
            color: var(--pdf-yellow-line);
        }}

        .topbar-search-box {{
            flex: 1;
            max-width: 380px;
            position: relative;
        }}

        .topbar-search-box input {{
            width: 100%;
            padding: 9px 14px 9px 36px;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            background: rgba(255, 255, 255, 0.15);
            color: #ffffff;
            font-size: 13px;
            outline: none;
            font-family: var(--font-sans);
        }}

        .topbar-search-box input:focus {{
            background: #ffffff;
            color: #000000;
            border-color: var(--pdf-yellow-line);
        }}

        .topbar-actions {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .btn-screen {{
            padding: 8px 18px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            border: none;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-family: var(--font-sans);
            transition: all 0.2s;
        }}

        .btn-screen-pdf {{
            background: var(--pdf-yellow-line);
            color: #0A3660;
            box-shadow: 0 3px 10px rgba(253, 184, 39, 0.4);
        }}

        .btn-screen-pdf:hover {{
            background: #e9a30f;
            transform: translateY(-1px);
        }}

        .btn-screen-feedback {{
            background: rgba(255, 255, 255, 0.15);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}

        .banner-guide {{
            background: #25282A;
            color: #cbd5e1;
            text-align: center;
            padding: 9px;
            font-size: 12.5px;
            border-bottom: 1px solid #383C40;
        }}

        .banner-guide strong {{
            color: var(--pdf-yellow-line);
        }}

        /* === EXACT A4 PAGES VIEWPORT === */
        .a4-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 30px 15px;
            gap: 30px;
        }}

        /* STRICT A4 SHEET: 210mm x 297mm */
        .a4-sheet {{
            width: 210mm;
            height: 297mm;
            min-height: 297mm;
            max-height: 297mm;
            background: #ffffff;
            box-sizing: border-box;
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.4);
            position: relative;
            overflow: hidden;
            page-break-after: always;
            break-after: page;
            page-break-inside: avoid;
            break-inside: avoid;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        /* === 1. CAPA (FRONT COVER) - PROMINENT DONA LU LOGO === */
        .a4-cover-page {{
            background: var(--pdf-blue-cover);
            color: #ffffff;
            padding: 22mm 20mm;
            position: relative;
        }}

        .cover-circle-bg {{
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.05);
            pointer-events: none;
        }}

        .circle-lg {{
            width: 360px;
            height: 360px;
            top: 50px;
            left: -90px;
        }}

        .circle-md {{
            width: 240px;
            height: 240px;
            top: 20px;
            right: 30px;
        }}

        .circle-sm {{
            width: 150px;
            height: 150px;
            bottom: 180px;
            right: 20px;
        }}

        .circle-bottom {{
            width: 290px;
            height: 290px;
            bottom: -60px;
            left: -60px;
        }}

        .cover-top-brand {{
            position: relative;
            z-index: 2;
            display: flex;
            align-items: center;
            gap: 16px;
        }}

        .cover-top-brand img {{
            height: 76px;
            width: 76px;
            border-radius: 16px;
            background: #ffffff;
            padding: 5px;
            box-shadow: 0 0 0 3px var(--pdf-yellow-line), 0 8px 25px rgba(0, 0, 0, 0.35);
            object-fit: contain;
        }}

        .cover-brand-title-wrap {{
            display: flex;
            flex-direction: column;
            gap: 3px;
        }}

        .cover-brand-title-main {{
            font-size: 24px;
            font-weight: 800;
            letter-spacing: 0.5px;
            color: #ffffff;
            text-transform: uppercase;
            line-height: 1.1;
        }}

        .cover-brand-title-sub {{
            font-size: 11.5px;
            font-weight: 700;
            color: var(--pdf-yellow-line);
            letter-spacing: 0.6px;
            text-transform: uppercase;
        }}

        .cover-hero-illustration {{
            display: flex;
            justify-content: center;
            align-items: flex-end;
            gap: 25px;
            margin: auto 0;
            position: relative;
            z-index: 2;
            height: 85mm;
        }}

        .hero-packshot-item {{
            max-height: 82mm;
            max-width: 50mm;
            object-fit: contain;
            filter: drop-shadow(0 15px 25px rgba(0, 0, 0, 0.45));
        }}

        .cover-title-group {{
            position: relative;
            z-index: 2;
            margin-top: auto;
        }}

        .cover-heading-main {{
            font-size: 42px;
            font-weight: 800;
            line-height: 1.15;
            letter-spacing: -1px;
            color: #ffffff;
            margin-bottom: 14px;
        }}

        .cover-subtitle-text {{
            font-size: 16px;
            font-weight: 600;
            color: #E2E8F0;
            margin-bottom: 16px;
        }}

        .cover-yellow-accent {{
            width: 90px;
            height: 6px;
            background: var(--pdf-yellow-line);
            border-radius: 3px;
            margin-bottom: 22px;
        }}

        .cover-footnote {{
            font-size: 12px;
            color: #CBD5E1;
            opacity: 0.9;
        }}

        /* === 2. APRESENTAÇÃO & SUMÁRIO === */
        .a4-toc-page {{
            padding: 0;
            background: #ffffff;
        }}

        /* PROMINENT BLUE HEADER BAR */
        .sheet-top-bar {{
            height: 16mm;
            background: var(--pdf-blue-bar);
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 16mm;
            flex-shrink: 0;
        }}

        .header-brand-side {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        /* PROMINENT HEADER LOGO */
        .header-logo-icon {{
            height: 44px;
            width: 44px;
            border-radius: 50%;
            background: #ffffff;
            padding: 1.5px;
            box-shadow: 0 0 0 2.5px var(--pdf-yellow-line);
            flex-shrink: 0;
            object-fit: cover;
        }}

        .header-brand-text-block {{
            display: flex;
            flex-direction: column;
        }}

        .header-brand-text {{
            font-size: 14.5px;
            font-weight: 800;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            line-height: 1.1;
        }}

        .header-brand-sub {{
            font-size: 9.5px;
            font-weight: 600;
            color: #CBD5E1;
            letter-spacing: 0.4px;
        }}

        .header-section-side {{
            display: flex;
            align-items: center;
        }}

        .header-seg-label {{
            background: rgba(253, 184, 39, 0.15);
            border: 1px solid var(--pdf-yellow-line);
            color: var(--pdf-yellow-line);
            font-size: 11px;
            font-weight: 800;
            padding: 3px 12px;
            border-radius: 20px;
            letter-spacing: 0.8px;
            text-transform: uppercase;
        }}

        .toc-inner-content {{
            padding: 16mm 18mm;
            display: flex;
            flex-direction: column;
            flex: 1;
        }}

        .toc-h2 {{
            font-size: 26px;
            font-weight: 800;
            color: var(--pdf-blue-title);
            margin-bottom: 12px;
            letter-spacing: -0.5px;
        }}

        .toc-p {{
            font-size: 14px;
            color: var(--pdf-text-dark);
            line-height: 1.6;
            margin-bottom: 26px;
        }}

        .toc-table-wrap {{
            display: flex;
            flex-direction: column;
        }}

        .toc-table-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid var(--pdf-border-line);
            font-size: 14px;
        }}

        .toc-col-title {{
            flex: 1;
            color: var(--pdf-text-dark);
            font-weight: 500;
        }}

        .toc-col-title strong {{
            color: var(--pdf-blue-title);
            font-weight: 800;
        }}

        .toc-col-cat {{
            color: #6B7280;
            margin-right: 25px;
            font-size: 13px;
            font-weight: 600;
        }}

        .toc-col-page {{
            font-weight: 800;
            color: var(--pdf-blue-title);
            width: 32px;
            text-align: right;
            font-size: 14px;
        }}

        /* RUNNING FOOTER */
        .sheet-footer-bar {{
            height: 12mm;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 16mm;
            font-size: 10.5px;
            color: #6B7280;
            flex-shrink: 0;
            border-top: 1px solid #E5E7EB;
        }}

        .footer-page-num {{
            font-weight: 800;
            color: var(--pdf-blue-title);
            font-size: 12px;
        }}

        /* === 3. PRODUCT PAGES - FIXED UNIFIED FLOW (ZERO GAP) === */
        .product-sheet {{
            padding: 0;
            background: #ffffff;
        }}

        .sheet-cards-stack {{
            padding: 8mm 14mm;
            display: flex;
            flex-direction: column;
            gap: 8mm;
            flex: 1;
            justify-content: space-between;
        }}

        /* EXACT CARD: 2 COLUMNS, SOFT BLUE BG, BUBBLES ON LEFT */
        .product-item-card {{
            background: var(--pdf-card-bg);
            border-radius: 18px;
            display: flex;
            height: 121mm;
            overflow: hidden;
            box-sizing: border-box;
            border: 1px solid #D1E5F5;
            position: relative;
        }}

        /* LEFT VISUAL COLUMN */
        .card-visual-col {{
            width: 37%;
            background: #F1F8FD;
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 15px;
            overflow: hidden;
        }}

        .bubble {{
            position: absolute;
            border-radius: 50%;
            background: var(--pdf-bubble-1);
            pointer-events: none;
        }}

        .bubble-1 {{
            width: 95px;
            height: 95px;
            top: 10px;
            left: 10px;
            opacity: 0.85;
        }}

        .bubble-2 {{
            width: 65px;
            height: 65px;
            bottom: 25px;
            right: 15px;
            background: var(--pdf-bubble-2);
        }}

        .bubble-3 {{
            width: 45px;
            height: 45px;
            top: 55px;
            right: 25px;
            opacity: 0.65;
        }}

        /* HIGH-RES PACKSHOT (EAGER LOADED) */
        .product-packshot-img {{
            max-height: 88mm;
            max-width: 90%;
            object-fit: contain;
            position: relative;
            z-index: 2;
            filter: drop-shadow(0 8px 14px rgba(10, 66, 117, 0.18));
        }}

        .product-brand-caption {{
            position: absolute;
            bottom: 8px;
            font-size: 10px;
            color: #6B7280;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            z-index: 3;
            background: rgba(255, 255, 255, 0.85);
            padding: 1px 8px;
            border-radius: 10px;
        }}

        /* RIGHT INFO COLUMN WITH HARMONIOUS VERTICAL CENTERING (ZERO GAP) */
        .card-info-col {{
            width: 64%;
            padding: 14px 22px 14px 20px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .card-title-header {{
            display: flex;
            flex-direction: column;
            gap: 6px;
            margin-bottom: 11px; /* Crisp, natural, fixed distance between badge and IDENTIFICAÇÃO */
        }}

        .prod-title {{
            font-size: 22px;
            font-weight: 800;
            color: var(--pdf-blue-title);
            line-height: 1.2;
            letter-spacing: -0.4px;
        }}

        .prod-badge-pill {{
            align-self: flex-start;
            background: var(--pdf-blue-pill);
            color: #ffffff;
            font-size: 11px;
            font-weight: 800;
            padding: 4px 13px;
            border-radius: 20px;
            text-transform: uppercase;
            letter-spacing: 0.7px;
        }}

        .meta-section {{
            display: flex;
            flex-direction: column;
            gap: 8px; /* Consistent rhythm matching the reference example */
        }}

        .meta-row {{
            display: flex;
            flex-direction: column;
            gap: 1.5px;
        }}

        .meta-lbl {{
            font-size: 11.5px;
            font-weight: 800;
            color: var(--pdf-blue-label);
            letter-spacing: 0.7px;
            text-transform: uppercase;
        }}

        .meta-txt {{
            font-size: 14.5px;
            color: var(--pdf-text-dark);
            line-height: 1.35;
        }}

        .pkg-highlight {{
            font-size: 15px;
            color: #001F56;
            font-weight: 600;
        }}

        .pkg-highlight strong {{
            color: #001F56;
            font-weight: 800;
        }}

        .directions-text {{
            font-size: 13.5px;
            color: #1F2937;
            font-weight: 500;
            line-height: 1.35;
        }}

        .active-highlight {{
            color: #004080;
            font-weight: 600;
            font-size: 13.5px;
        }}

        .card-btn-strip {{
            display: flex;
            gap: 6px;
            align-items: center;
            margin-top: 10px;
        }}

        .btn-wa-compact {{
            background: var(--donalu-whatsapp);
            color: #ffffff;
            font-size: 10.5px;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 4px;
            text-decoration: none;
            white-space: nowrap;
        }}

        .btn-site-compact {{
            background: #ffffff;
            color: var(--pdf-blue-pill);
            border: 1px solid #BEE3F8;
            font-size: 10.5px;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 4px;
            text-decoration: none;
            white-space: nowrap;
        }}

        .btn-feedback-compact {{
            background: #E2E8F0;
            border: 1px solid #CBD5E1;
            color: #334155;
            font-size: 10.5px;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            white-space: nowrap;
        }}

        /* === 4. CONTRA-CAPA (BACK COVER) - LARGE PROMINENT DONA LU LOGO === */
        .a4-back-page {{
            background: var(--pdf-blue-cover);
            color: #ffffff;
            padding: 24mm 20mm;
            position: relative;
        }}

        /* PROMINENT BACK COVER LOGO */
        .back-cover-logo-prominent {{
            width: 170px;
            height: 170px;
            border-radius: 24px;
            background: #ffffff;
            padding: 12px;
            box-shadow: 0 0 0 4px var(--pdf-yellow-line), 0 14px 35px rgba(0,0,0,0.4);
            margin-bottom: 24px;
            object-fit: contain;
            display: block;
        }}

        .back-heading-fale {{
            font-size: 42px;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 12px;
            letter-spacing: -1px;
        }}

        .back-contact-list {{
            display: flex;
            flex-direction: column;
            gap: 12px;
            font-size: 16px;
            color: #E2E8F0;
            position: relative;
            z-index: 2;
        }}

        .back-contact-list a {{
            color: #ffffff;
            text-decoration: none;
            transition: color 0.2s;
        }}

        .back-contact-list a:hover {{
            color: var(--pdf-yellow-line);
        }}

        .back-disclaimer {{
            font-size: 12px;
            color: #CBD5E1;
            position: relative;
            z-index: 2;
            line-height: 1.5;
        }}

        /* === MODAL & PALPITES DRAWER === */
        .modal-bg {{
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(10, 54, 96, 0.75);
            backdrop-filter: blur(4px);
            z-index: 2000;
            display: none;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}

        .modal-card {{
            background: #ffffff;
            border-radius: 12px;
            width: 100%;
            max-width: 480px;
            padding: 24px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            border-top: 5px solid var(--pdf-yellow-line);
        }}

        .drawer-bg {{
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0, 0, 0, 0.4);
            z-index: 1500;
            display: none;
        }}

        .feedback-flyout {{
            position: fixed;
            top: 0; right: 0;
            width: 420px;
            max-width: 90vw;
            height: 100vh;
            background: #ffffff;
            z-index: 1600;
            box-shadow: -10px 0 30px rgba(0,0,0,0.25);
            transform: translateX(100%);
            transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex;
            flex-direction: column;
        }}

        .feedback-flyout.open {{
            transform: translateX(0);
        }}

        /* === STRICT A4 PRINT RULES: ZERO SLICING & CLEAN CONTINUOUS METADATA === */
        @page {{
            size: A4 portrait;
            margin: 0;
        }}

        @media print {{
            html, body {{
                margin: 0 !important;
                padding: 0 !important;
                background: #ffffff !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }}

            .screen-topbar,
            .banner-guide,
            .card-btn-strip,
            .modal-bg,
            .drawer-bg,
            .feedback-flyout {{
                display: none !important;
            }}

            .a4-container {{
                padding: 0 !important;
                gap: 0 !important;
            }}

            .a4-sheet {{
                width: 210mm !important;
                height: 297mm !important;
                min-height: 297mm !important;
                max-height: 297mm !important;
                margin: 0 !important;
                box-shadow: none !important;
                border: none !important;
                page-break-after: always !important;
                break-after: page !important;
                page-break-inside: avoid !important;
                break-inside: avoid !important;
                overflow: hidden !important;
            }}

            .a4-cover-page {{
                padding: 22mm 20mm !important;
            }}

            .a4-back-page {{
                padding: 24mm 20mm !important;
            }}

            .product-sheet {{
                padding: 0 !important;
            }}

            .sheet-cards-stack {{
                padding: 8mm 14mm !important;
                height: 269mm !important;
            }}

            .product-item-card {{
                height: 121mm !important;
                box-shadow: none !important;
            }}

            .card-info-col {{
                justify-content: center !important; /* Vertically centered, perfectly balanced */
                padding: 12mm 16mm !important;
            }}

            * {{
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }}
        }}
    </style>
</head>
<body>

    <!-- SCREEN TOPBAR (CONTROLS & PALPITES) -->
    <header class="screen-topbar">
        <div class="topbar-wrapper">
            <a href="#" class="brand-link">
                <img src="assets_donalu/dona-lu-avatar-smooth.png" alt="Dona Lu Logo" class="brand-logo-circle">
                <div class="brand-text-name">DONA LU <span>MATERIAIS</span></div>
            </a>

            <div class="topbar-search-box">
                <input type="text" id="liveSearch" placeholder="Localizar produto por nome, ativo ou embalagem..." oninput="filterCards()">
            </div>

            <div class="topbar-actions">
                <button class="btn-screen btn-screen-pdf" onclick="window.print()">
                    <span>🖨️</span> Salvar em PDF (A4)
                </button>
                <button class="btn-screen btn-screen-feedback" onclick="toggleDrawer()">
                    <span>💬</span> Palpites (<span id="feedbackCounter">0</span>)
                </button>
            </div>
        </div>
    </header>

    <div class="banner-guide">
        ✨ <strong>Espaçamento Harmonizado:</strong> O vão vago entre a pílula de categoria e a identificação foi completamente eliminado. O texto agora flui de forma unificada, limpa e contínua, exatamente como no modelo gráfico profissional.
    </div>

    <!-- MAIN SHEETS CONTAINER (43 FOLHAS A4) -->
    <main class="a4-container">

        <!-- PÁGINA 1: CAPA (FRONT COVER) -->
        <div class="a4-sheet a4-cover-page">
            <div class="cover-circle-bg circle-lg"></div>
            <div class="cover-circle-bg circle-md"></div>
            <div class="cover-circle-bg circle-sm"></div>
            <div class="cover-circle-bg circle-bottom"></div>

            <div class="cover-top-brand">
                <img src="assets_donalu/dona-lu-smooth-960.png" alt="Logo Dona Lu">
                <div class="cover-brand-title-wrap">
                    <span class="cover-brand-title-main">DONA LU MATERIAIS</span>
                    <span class="cover-brand-title-sub">Distribuidora Autorizada Start Química</span>
                </div>
            </div>

            <!-- CENTER FEATURED PACKSHOTS -->
            <div class="cover-hero-illustration">
                <img src="{featured_packshots[0]}" alt="Produto Destaque 1" loading="eager" class="hero-packshot-item">
                <img src="{featured_packshots[1]}" alt="Produto Destaque 2" loading="eager" class="hero-packshot-item" style="max-height: 87mm; z-index:3;">
                <img src="{featured_packshots[2]}" alt="Produto Destaque 3" loading="eager" class="hero-packshot-item">
            </div>

            <div class="cover-title-group">
                <h1 class="cover-heading-main">
                    Catálogo de<br>Produtos de Limpeza
                </h1>
                <div class="cover-subtitle-text">
                    Linha profissional e doméstica | 2026
                </div>
                <div class="cover-yellow-accent"></div>
                <div class="cover-footnote">
                    Dona Lu Materiais de Limpeza · Distribuidora Autorizada Start Química · São José do Rio Preto, SP
                </div>
            </div>
        </div>

        <!-- PÁGINA 2: APRESENTAÇÃO & SUMÁRIO -->
        <div class="a4-sheet a4-toc-page">
            <header class="sheet-top-bar">
                <div class="header-brand-side">
                    <img src="assets_donalu/dona-lu-avatar-smooth.png" alt="Logo Dona Lu" class="header-logo-icon">
                    <div class="header-brand-text-block">
                        <span class="header-brand-text">DONA LU MATERIAIS</span>
                        <span class="header-brand-sub">Limpeza Profissional · Distribuidora Start Química</span>
                    </div>
                </div>
                <div class="header-section-side">
                    <span class="header-seg-label">Apresentação</span>
                </div>
            </header>

            <div class="toc-inner-content">
                <div style="display: flex; align-items: center; gap: 20px; background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 5px solid var(--pdf-yellow-line); border-radius: 14px; padding: 14px 18px; margin-bottom: 12px;">
                    <img src="assets_donalu/dona-lu-smooth-960.png" alt="Dona Lu Materiais" style="width: 100px; height: 100px; border-radius: 14px; background: #ffffff; padding: 6px; border: 1.5px solid #CBD5E1; object-fit: contain; flex-shrink: 0; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
                    <div style="flex: 1;">
                        <h2 class="toc-h2" style="margin-bottom: 6px;">Quem somos</h2>
                        <p class="toc-p" style="margin-bottom: 0;">
                            A <strong>Dona Lu</strong> é a sua distribuidora de produtos de limpeza profissional em São José do Rio Preto e região. Oferecemos assessoria técnica para diluição inteligente e redução de custos, soluções completas para limpeza pós-obra, atendimento a empresas, condomínios e residências, além de locação de máquinas de limpeza. Em parceria com a <strong>Start Química</strong>, este catálogo reúne 80 soluções essenciais com alto poder de desincrustação e conformidade técnica.
                        </p>
                    </div>
                </div>

                <h2 class="toc-h2" style="margin-top: 10px;">Sumário de Linhas</h2>
                <div class="toc-table-wrap">
                    {''.join(toc_rows_html)}
                </div>
            </div>

            <footer class="sheet-footer-bar">
                <div class="footer-left-note">
                    Catálogo de Produtos de Limpeza 2026 | Dona Lu Materiais · Distribuidora Start Química
                </div>
                <div class="footer-page-num">
                    2
                </div>
            </footer>
        </div>

        <!-- PÁGINAS 3 A 42: OS 80 PRODUTOS (2 POR PÁGINA COM ESPAÇAMENTO CONTÍGUO) -->
        {''.join(product_sheets_html)}

        <!-- PÁGINA 43: CONTRA-CAPA (FALE COM A GENTE COM LOGO DESTACADA) -->
        <div class="a4-sheet a4-back-page">
            <div class="cover-circle-bg circle-lg"></div>
            <div class="cover-circle-bg circle-md"></div>
            <div class="cover-circle-bg circle-bottom"></div>

            <div class="cover-top-brand">
                <img src="assets_donalu/dona-lu-smooth-960.png" alt="Logo Dona Lu">
                <div class="cover-brand-title-wrap">
                    <span class="cover-brand-title-main">DONA LU MATERIAIS</span>
                    <span class="cover-brand-title-sub">Distribuidora Autorizada Start Química</span>
                </div>
            </div>

            <div style="margin: auto 0; position: relative; z-index: 2;">
                <!-- PROMINENT DONA LU LOGO -->
                <img src="assets_donalu/dona-lu-smooth-960.png" alt="Dona Lu Logo Oficial" class="back-cover-logo-prominent">

                <h2 class="back-heading-fale">Fale com a gente</h2>
                <div class="cover-yellow-accent"></div>

                <div class="back-contact-list">
                    <div><strong>WhatsApp:</strong> <a href="https://wa.me/5517981321919" target="_blank">(17) 98132-1919</a></div>
                    <div><strong>E-mail:</strong> donalumateriais@gmail.com</div>
                    <div><strong>Site:</strong> donalu.com.br</div>
                    <div><strong>Instagram:</strong> <a href="https://www.instagram.com/donalumateriaisdelimpeza/" target="_blank">@donalumateriaisdelimpeza</a></div>
                    <div><strong>Cidade:</strong> São José do Rio Preto, SP</div>
                </div>
            </div>

            <div class="back-disclaimer">
                Preços, disponibilidade e composições sujeitos a alteração. Consulte a FISPQ de cada produto.<br>
                &copy; 2026 Dona Lu Materiais de Limpeza · CNPJ 69.236.751/0001-08 · Distribuidora Autorizada Start Química.
            </div>
        </div>

    </main>

    <!-- MODAL DE PALPITE -->
    <div class="modal-bg" id="commentModal" onclick="closeCommentModal(event)">
        <div class="modal-card" onclick="event.stopPropagation()">
            <h3 style="font-size: 18px; font-weight:800; color:var(--pdf-blue-title); margin-bottom:4px;" id="modalTitle">Deixar Palpite</h3>
            <p style="font-size: 12.5px; color:#64748B; margin-bottom:14px;">Envie uma sugestão sobre este produto:</p>
            
            <textarea id="modalText" style="width:100%; height:90px; border:1px solid #CBD5E0; border-radius:6px; padding:10px; font-family:var(--font-sans); font-size:13px; outline:none; margin-bottom:12px;" placeholder="Ex: Ajustar indicação, dar destaque na embalagem de 5L..."></textarea>
            
            <div style="display:flex; justify-content:flex-end; gap:8px;">
                <button class="btn-screen" style="background:#EDF2F7; color:#4A5568;" onclick="closeCommentModal()">Cancelar</button>
                <button class="btn-screen btn-screen-pdf" onclick="saveComment()">Salvar Palpite</button>
            </div>
        </div>
    </div>

    <!-- FLYOUT DE PALPITES -->
    <div class="drawer-bg" id="drawerBg" onclick="toggleDrawer()"></div>
    <div class="feedback-flyout" id="feedbackDrawer">
        <div style="padding:18px 20px; background:var(--pdf-blue-bar); color:#ffffff; display:flex; justify-content:space-between; align-items:center;">
            <h3 style="font-size:16px; font-weight:800;">📝 Painel de Palpites & Feedback</h3>
            <button onclick="toggleDrawer()" style="background:none; border:none; color:var(--pdf-yellow-line); font-size:22px; cursor:pointer;">&times;</button>
        </div>
        <div style="padding:20px; overflow-y:auto; flex:1;" id="drawerList">
            <p style="color:#64748B; font-size:13px;">Nenhum palpite salvo ainda.</p>
        </div>
        <div style="padding:14px 20px; border-top:1px solid #E2E8F0; display:flex; gap:8px; background:#F7FAFC;">
            <button class="btn-screen btn-screen-pdf" style="flex:1;" onclick="copyFeedback()">📋 Copiar Resumo</button>
            <button class="btn-screen" style="background:#EDF2F7; color:#4A5568;" onclick="clearFeedback()">Limpar</button>
        </div>
    </div>

    <script>
        let feedbackData = JSON.parse(localStorage.getItem('donalu_feedbacks_pdf_style') || '{{}}');
        let currentId = null;

        function updateUI() {{
            const keys = Object.keys(feedbackData);
            document.getElementById('feedbackCounter').innerText = keys.length;
            const list = document.getElementById('drawerList');
            if (keys.length === 0) {{
                list.innerHTML = '<p style="color:#64748B; font-size:13px; text-align:center; padding:20px 0;">Nenhum palpite ainda.<br>Clique no botão <strong>"💬 Palpite"</strong> em qualquer produto para sugerir alterações.</p>';
                return;
            }}
            let html = '';
            keys.forEach(id => {{
                const item = feedbackData[id];
                html += `
                    <div style="background:#F7FAFC; border:1px solid #E2E8F0; border-radius:6px; padding:10px; margin-bottom:10px;">
                        <strong style="font-size:13px; color:#111827;">#${{String(id).padStart(3, '0')}} - ${{item.name}}</strong>
                        <p style="font-size:12px; color:#4B5563; margin-top:4px;">${{item.text}}</p>
                    </div>
                `;
            }});
            list.innerHTML = html;
            localStorage.setItem('donalu_feedbacks_pdf_style', JSON.stringify(feedbackData));
        }}

        function openCommentModal(id) {{
            currentId = id;
            const card = document.querySelector(`.product-item-card[data-id="${{id}}"]`);
            const title = card.querySelector('.prod-title').innerText;
            document.getElementById('modalTitle').innerText = '#' + String(id).padStart(3, '0') + ' - ' + title;
            document.getElementById('modalText').value = (feedbackData[id] && feedbackData[id].text) || '';
            document.getElementById('commentModal').style.display = 'flex';
        }}

        function closeCommentModal(e) {{
            if (e && e.target !== document.getElementById('commentModal')) return;
            document.getElementById('commentModal').style.display = 'none';
        }}

        function saveComment() {{
            if (!currentId) return;
            const card = document.querySelector(`.product-item-card[data-id="${{currentId}}"]`);
            const title = card.querySelector('.prod-title').innerText;
            const text = document.getElementById('modalText').value.trim();
            if (text) {{
                feedbackData[currentId] = {{ name: title, text: text }};
            }} else {{
                delete feedbackData[currentId];
            }}
            document.getElementById('commentModal').style.display = 'none';
            updateUI();
        }}

        function toggleDrawer() {{
            const drawer = document.getElementById('feedbackDrawer');
            const bg = document.getElementById('drawerBg');
            if (drawer.classList.contains('open')) {{
                drawer.classList.remove('open');
                bg.style.display = 'none';
            }} else {{
                drawer.classList.add('open');
                bg.style.display = 'block';
            }}
        }}

        function copyFeedback() {{
            const keys = Object.keys(feedbackData);
            if (!keys.length) return alert('Nenhum palpite para copiar.');
            let msg = '=== PALPITES DO CATÁLOGO DONA LU ===\\n\\n';
            keys.forEach(k => {{
                msg += `#${{String(k).padStart(3, '0')}} - ${{feedbackData[k].name}}\\nSugestão: ${{feedbackData[k].text}}\\n--------------------\\n`;
            }});
            navigator.clipboard.writeText(msg).then(() => alert('Palpites copiados com sucesso!'));
        }}

        function clearFeedback() {{
            if (confirm('Limpar todos os palpites?')) {{
                feedbackData = {{}};
                updateUI();
            }}
        }}

        function filterCards() {{
            const q = document.getElementById('liveSearch').value.toLowerCase().trim();
            document.querySelectorAll('.product-item-card').forEach(c => {{
                const text = c.innerText.toLowerCase();
                c.style.opacity = (!q || text.includes(q)) ? '1' : '0.2';
            }});
        }}

        updateUI();
    </script>
</body>
</html>
"""

with open('catalogo_visual.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print("Espaçamento corrigido com sucesso em catalogo_visual.html!")
