# Catálogo de Produtos de Limpeza 2026 — Dona Lu Materiais

Catálogo comercial e técnico completo de produtos de limpeza profissional e doméstica para a **Dona Lu Materiais** (Distribuidora Autorizada **Start Química** em São José do Rio Preto e região).

---

## 📋 Conteúdo do Repositório

- **`catalogo_visual.html`**: Catálogo interativo responsivo diagramado estritamente em padrão **A4** (2 produtos por página), com botões de pedido direto via WhatsApp, link para ficha técnica Start Química e sistema de anotação de palpites/revisões.
- **`catalogo_donalu_final.pdf`**: Catálogo completo compilado em PDF com 43 páginas (Capa, Apresentação/Sumário, 40 páginas de produtos e Contra-capa).
- **`imagens_produtos/`**: Pasta contendo os **80 packshots oficiais** em alta resolução com fundo transparente (`.png`).
- **`assets_donalu/`**: Identidade visual, logotipo vetorizado/HD e avatares tratados da **Dona Lu Materiais**.
- **`catalogo_detalhado.json`**: Base de dados estruturada em JSON com todas as informações técnicas dos 80 itens (código, nome, marca, segmento, embalagem/litragens, indicação de uso resumida, fragrância, ativos químicos e URLs oficiais).
- **`catalogo_produtos.csv`**: Planilha tabular completa pronta para importação em Excel ou sistemas ERP.
- **`gerar_catalogo_identico_ao_exemplo.py`**: Script mestre em Python para geração automatizada do catálogo HTML diagramado em A4 sem quebra de páginas.
- **`render_pdf.py`**: Script de automação para compilação direta do HTML em PDF A4 via motor headless Chromium.
- **`baixar_catalogo.py` / `coletar_dados_completos.py`**: Scripts de extração e coleta de dados da Start Química.

---

## 🗂️ Linhas de Produtos Contempladas

1. **Pisos & Pedras** (10 produtos)
2. **Desinfecção & Limpeza Geral Multiuso** (28 produtos)
3. **Lavanderia & Tratamento de Roupas** (18 produtos)
4. **Cozinha & Louças** (7 produtos)
5. **Higiene Pessoal & Asseptgel** (5 produtos)
6. **Aromatizantes & Linha Pet** (7 produtos)
7. **Automotiva (Indy Cryl)** (5 produtos)

---

## 🚀 Como Visualizar ou Gerar o PDF

### Visualização Rápida no Navegador:
Abra o arquivo `catalogo_visual.html` em qualquer navegador moderno (Chrome, Edge, Firefox, Safari).

### Gerar Novo PDF via Terminal:
```bash
python render_pdf.py
```
Ou abra `catalogo_visual.html` no navegador e selecione **Imprimir (Ctrl+P)** -> **Salvar como PDF** com layout Retrato e margens em Nenhuma.

---

© 2026 Dona Lu Materiais de Limpeza · Distribuidora Autorizada Start Química.
