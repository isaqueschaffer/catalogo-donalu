from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

img = Image.open("img-dona-lu.jpg").convert("RGB")
print("Original size:", img.size)

# 1. Upscale using Lanczos to 960x960 (4x)
img_large = img.resize((960, 960), Image.Resampling.LANCZOS)

# 2. Clean white background: anywhere with near-white (r>240, g>240, b>240) in outer regions becomes pure white (255, 255, 255)
arr = np.array(img_large)
# threshold for white
is_white = (arr[:, :, 0] > 242) & (arr[:, :, 1] > 242) & (arr[:, :, 2] > 242)
arr[is_white] = [255, 255, 255]

cleaned = Image.fromarray(arr)

# 3. Enhance sharpness slightly
enhancer = ImageEnhance.Sharpness(cleaned)
sharpened = enhancer.enhance(1.4)

# 4. Enhance contrast slightly
enhancer_c = ImageEnhance.Contrast(sharpened)
contrast = enhancer_c.enhance(1.08)

contrast.save("assets_donalu/img-dona-lu-hd.png", "PNG")
print("Saved assets_donalu/img-dona-lu-hd.png")

# 5. Create transparent PNG version
rgba = contrast.convert("RGBA")
data = np.array(rgba)
# pure white -> transparent
alpha_mask = (data[:, :, 0] > 248) & (data[:, :, 1] > 248) & (data[:, :, 2] > 248)
data[alpha_mask, 3] = 0
# smooth edge alpha for anti-aliasing
rgba_clean = Image.fromarray(data)
rgba_clean.save("assets_donalu/img-dona-lu-transparent.png", "PNG")
print("Saved assets_donalu/img-dona-lu-transparent.png")

# 6. Create focused avatar crop for small circular headers (focused on her smiling face and apron)
# Let's crop around center (x: 240 to 650, y: 50 to 580)
avatar_crop = contrast.crop((230, 50, 680, 500))
avatar_hd = avatar_crop.resize((400, 400), Image.Resampling.LANCZOS)
avatar_hd.save("assets_donalu/img-dona-lu-avatar.png", "PNG")
print("Saved assets_donalu/img-dona-lu-avatar.png")

