#!/usr/bin/env python3
"""Render an OpenPose (18 keypoint, body25-less) skeleton with the standard colours.
Keypoints (x, y) in a 0..1 frame; None = missing.  Order:
0 nose, 1 neck, 2 Rsho, 3 Relb, 4 Rwri, 5 Lsho, 6 Lelb, 7 Lwri,
8 Rhip, 9 Rkne, 10 Rank, 11 Lhip, 12 Lkne, 13 Lank, 14 Reye, 15 Leye, 16 Rear, 17 Lear
("R" = the person's right, drawn on the viewer's left when facing the camera)."""
from PIL import Image, ImageDraw
LIMBS = [(1,2),(1,5),(2,3),(3,4),(5,6),(6,7),(1,8),(8,9),(9,10),(1,11),(11,12),(12,13),
         (1,0),(0,14),(14,16),(0,15),(15,17)]
COLORS = [(255,0,0),(255,85,0),(255,170,0),(255,255,0),(170,255,0),(85,255,0),(0,255,0),
          (0,255,85),(0,255,170),(0,255,255),(0,170,255),(0,85,255),(0,0,255),(85,0,255),
          (170,0,255),(255,0,255),(255,0,170),(255,0,85)]
def render(kps, size=512, out="pose.png"):
    im = Image.new("RGB", (size, size), "black"); d = ImageDraw.Draw(im)
    w = max(4, size // 100); r = max(4, size // 96)
    P = [None if k is None else (k[0]*size, k[1]*size) for k in kps]
    for (a, b), c in zip(LIMBS, COLORS):
        if P[a] and P[b]:
            d.line([P[a], P[b]], fill=c, width=w)
    for i, p in enumerate(P):
        if p:
            d.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], fill=COLORS[i % len(COLORS)])
    im.save(out); return out
if __name__ == "__main__":
    # Peace sign toward the camera: person's right arm bent, forearm foreshortened,
    # wrist beside the right eye; left arm relaxed; legs slightly apart.
    peace = [
        (0.50,0.20),  # 0 nose
        (0.50,0.30),  # 1 neck
        (0.415,0.31), # 2 R shoulder (viewer left)
        (0.36,0.44),  # 3 R elbow (down and out)
        (0.42,0.24),  # 4 R wrist beside the face (foreshortened forearm toward camera)
        (0.585,0.31), # 5 L shoulder
        (0.62,0.46),  # 6 L elbow
        (0.63,0.60),  # 7 L wrist
        (0.455,0.58), # 8 R hip
        (0.44,0.76),  # 9 R knee
        (0.43,0.94),  # 10 R ankle
        (0.545,0.58), # 11 L hip
        (0.565,0.76), # 12 L knee
        (0.58,0.94),  # 13 L ankle
        (0.48,0.18),  # 14 R eye
        (0.52,0.18),  # 15 L eye
        (0.455,0.19), # 16 R ear
        (0.545,0.19), # 17 L ear
    ]
    for s in (512, 768):
        render(peace, s, f"dt_test/openpose_peace_{s}.png")
    print("rendered")
