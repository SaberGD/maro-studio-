import numpy as np
from PIL import Image, ImageFilter
blue = Image.open('user/blue.jpg').convert('RGB')
red = Image.open('user/red.webp').convert('RGB')
cut = Image.open('user/cutout.webp').convert('RGBA')

def bbox(path, cut_x=0.8):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    m = (a[..., 2] - a[..., 0] > 40) & (a[..., 2] > 90)   # the blue wall
    H, W = m.shape
    m[:, int(W * cut_x):] = False   # ignore swatches/panels on the right
    ys, xs = np.where(m)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1

def checker(w, h, s):
    y, x = np.mgrid[0:h, 0:w]
    c = (((x // s) + (y // s)) % 2) * 51 + 204
    return Image.fromarray(np.stack([c] * 3, -1).astype(np.uint8))

def ants(alpha, s):
    a = np.asarray(alpha) > 128
    er = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(2 * s + 1))) > 0
    e = a & ~er
    h, w = a.shape
    y, x = np.mgrid[0:h, 0:w]
    dash = ((x + y) // (4 * s)) % 2 == 0
    return e, dash

def composite(src_shot, box, layer, out, dialog_from=None, ant=False, dialog_rect=None):
    shot = Image.open(src_shot).convert('RGB')
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    tile = layer.resize((w, h), Image.LANCZOS)
    region = np.asarray(shot.crop(box)).copy()
    new = np.asarray(tile).copy()
    if ant:
        al = cut.split()[3].resize((w, h), Image.LANCZOS)
        e, dash = ants(al, max(1, round(w / 600)))
        new[e & dash] = 0; new[e & ~dash] = 255
    if dialog_from:   # keep the dialog: the box where the shot differs from the same view without it
        ref = np.asarray(Image.open(dialog_from).convert('RGB').crop(box)).astype(int)
        diff = np.abs(region.astype(int) - ref).sum(-1) > 60
        ys, xs = np.where(diff)
        if dialog_rect is None:
            dialog_rect = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        a0, b0, a1, b1 = dialog_rect
        new[b0:b1, a0:a1] = region[b0:b1, a0:a1]
    shot.paste(Image.fromarray(new), (x0, y0))
    shot.save(out)
    return dialog_rect if dialog_from else None

def cutout_on_checker(w, h, s):
    c = checker(w, h, s)
    c.paste(cut.resize((w, h), Image.LANCZOS), (0, 0), cut.resize((w, h), Image.LANCZOS))
    return c

B = bbox('hero/11-open.png'); print('1x box', B)
w, h = B[2] - B[0], B[3] - B[1]
composite('hero/11-open.png', B, blue, 'fix/11-open.png')
composite('hero/11-open.png', B, blue, 'fix/12-subject.png', ant=True)
composite('hero/14-cutout.png', B, cutout_on_checker(w, h, 8), 'fix/14-cutout.png')
composite('hero/15-both.png', B, blue, 'fix/15-both.png')
DR = composite('hero/16-hs-open.png', B, blue, 'fix/16-hs-open.png', dialog_from='hero/15-both.png'); print('dialog', DR)
composite('hero/17-hs-hue.png', B, red, 'fix/17-hs-hue.png', dialog_from='hero/15-both.png', dialog_rect=DR)
composite('hero/18-final.png', B, red, 'fix/18-final.png')
# the Background layer thumbnail in the Layers panel still shows the yellow wall: recolour yellow -> wall red
for f in ['fix/17-hs-hue.png', 'fix/18-final.png']:
    im = Image.open(f).convert('RGB'); a = np.asarray(im).copy()
    p = a[300:560, 1500:1920].astype(int)
    yel = (p[..., 0] > 120) & (p[..., 1] > 90) & (p[..., 2] < 80)
    p[yel] = (np.array([170, 20, 45]) * (p[yel].sum(-1, keepdims=True) / 380.0)).clip(0, 255)
    a[300:560, 1500:1920] = p; Image.fromarray(a.astype(np.uint8)).save(f)
for n in ['11-open', '12-subject', '14-cutout', '18-final']:
    Image.open(f'fix/{n}.png').crop(B).save(f'fix/crop-{n}.png')
HB = bbox('hd/02-open.png', 0.55); print('hd box', HB)
composite('hd/02-open.png', HB, blue, 'fix/hd-ants.png', ant=True)
composite('hd/cmd-SelectSubject.png', HB, blue, 'fix/hd-cmd.png', dialog_from='hd/02-open.png')
