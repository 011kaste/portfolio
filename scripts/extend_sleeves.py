from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from pathlib import Path

FILES = [
    Path("assets/idle.jpg"),
    Path("assets/speak2.jpg"),
    Path("assets/speak3.jpg"),
    Path("assets/speak4.jpg"),
]

def poly_mask(size, points, feather=3.0):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.polygon(points, fill=255)
    if feather:
        m = m.filter(ImageFilter.GaussianBlur(feather))
    return m

def sleeve_layer(im, seed=1):
    arr = np.asarray(im).astype(np.float32)
    h, w = arr.shape[:2]
    gray = arr.mean(axis=2)

    # Preserve the arm's original light/shadow so the new fabric still follows
    # the existing form, but remap it into charcoal-black denim values.
    local = (gray - 70.0) / 130.0
    local = np.clip(local, 0.0, 1.0)
    base = 28.0 + local * 34.0

    rng = np.random.default_rng(seed)
    noise = rng.normal(0, 2.4, (h, w))
    fabric = np.clip(base + noise, 18, 68)
    out = np.stack([fabric * 0.92, fabric * 0.94, fabric], axis=2)

    # Very subtle vertical/diagonal denim grain.
    yy, xx = np.mgrid[0:h, 0:w]
    weave = 1.6*np.sin((xx + yy*0.35)/5.0) + 1.0*np.sin((xx*0.3 - yy)/9.0)
    out += weave[..., None]
    return Image.fromarray(np.uint8(np.clip(out, 0, 255)), "RGB")

def add_wrinkles(layer, masks):
    shade = Image.new("RGBA", layer.size, (0,0,0,0))
    hi = Image.new("RGBA", layer.size, (0,0,0,0))
    ds = ImageDraw.Draw(shade)
    dh = ImageDraw.Draw(hi)

    # Fine folds following the resting forearms.
    dark_lines = [
        [(565,500),(625,520),(684,532),(730,548)],
        [(583,514),(640,536),(695,548)],
        [(1035,500),(975,520),(916,532),(870,548)],
        [(1016,514),(960,536),(905,548)],
    ]
    light_lines = [
        [(575,492),(635,511),(695,525)],
        [(1025,492),(965,511),(905,525)],
    ]
    for pts in dark_lines:
        ds.line(pts, fill=(0,0,0,34), width=5)
    for pts in light_lines:
        dh.line(pts, fill=(255,255,255,18), width=3)

    shade = shade.filter(ImageFilter.GaussianBlur(4))
    hi = hi.filter(ImageFilter.GaussianBlur(3))

    total_mask = Image.new("L", layer.size, 0)
    for m in masks:
        total_mask = Image.fromarray(np.maximum(np.asarray(total_mask), np.asarray(m)).astype(np.uint8))
    shade.putalpha(Image.fromarray((np.asarray(shade.getchannel("A")) * (np.asarray(total_mask)/255.0)).astype(np.uint8)))
    hi.putalpha(Image.fromarray((np.asarray(hi.getchannel("A")) * (np.asarray(total_mask)/255.0)).astype(np.uint8)))

    layer = Image.alpha_composite(layer.convert("RGBA"), shade)
    layer = Image.alpha_composite(layer, hi)
    return layer.convert("RGB")

def edit(path, seed):
    im = Image.open(path).convert("RGB")
    if im.size != (1600, 900):
        raise ValueError(f"Unexpected size for {path}: {im.size}")

    # Masks hug only the visible tattooed forearms. Hands and existing jacket
    # remain untouched; cuff ends stop immediately before the wrists/hands.
    left = poly_mask(im.size, [
        (522,477),(548,463),(594,473),(646,492),(700,510),
        (744,526),(771,548),(761,568),(733,575),(691,566),
        (646,553),(598,541),(552,529),(523,514)
    ], 2.6)

    right = poly_mask(im.size, [
        (1078,477),(1052,463),(1006,473),(954,492),(900,510),
        (856,526),(829,548),(839,568),(867,575),(909,566),
        (954,553),(1002,541),(1048,529),(1077,514)
    ], 2.6)

    fabric = sleeve_layer(im, seed)
    fabric = add_wrinkles(fabric, [left, right])

    out = im.copy()
    out.paste(fabric, (0,0), left)
    out.paste(fabric, (0,0), right)

    # Cuff definition near each wrist, kept soft and narrow.
    cuff = Image.new("RGBA", im.size, (0,0,0,0))
    dc = ImageDraw.Draw(cuff)
    dc.line([(731,555),(748,563),(761,562)], fill=(8,8,9,115), width=3)
    dc.line([(869,555),(852,563),(839,562)], fill=(8,8,9,115), width=3)
    cuff = cuff.filter(ImageFilter.GaussianBlur(1.2))
    out = Image.alpha_composite(out.convert("RGBA"), cuff).convert("RGB")

    out.save(path, "JPEG", quality=95, subsampling=0, optimize=True)

for i, f in enumerate(FILES, 11):
    edit(f, i)
    print(f"updated {f}")
