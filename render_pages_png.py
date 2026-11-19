import fitz # PyMuPDF
import os

# 1. Render page 1 (or 2) of the example PDF
doc_ex = fitz.open("catalogo_limpeza_exemplo (1).pdf")
print("Example PDF pages:", len(doc_ex))
for i in range(len(doc_ex)):
    page = doc_ex[i]
    pix = page.get_pixmap(dpi=150)
    out_name = f"exemplo_page_{i+1}.png"
    pix.save(out_name)
    print(f"Saved {out_name}")

# 2. Render page 3 of our generated PDF
doc_our = fitz.open("catalogo_donalu_final.pdf")
print("Our PDF pages:", len(doc_our))
page3 = doc_our[2] # 0-indexed, page 3 has product #001 and #002 (Sabão de Querosene)
pix3 = page3.get_pixmap(dpi=150)
pix3.save("our_page_3.png")
print("Saved our_page_3.png")

