#!/usr/bin/env python3
"""Split the CLIP-L, CLIP-G and VAE weights embedded in an SDXL checkpoint into
separate safetensors files, so that `draw-things-cli models import` can be given
them explicitly (workaround for draw-things-community issue #107).

Usage: python3 extract_sdxl_companions.py model.safetensors
Writes clip_l.safetensors, clip_g.safetensors and vae.safetensors next to it.
Pure Python, no dependencies."""
import json, struct, sys, os

# (output file, key prefix in the checkpoint, strip the prefix in the output?)
# The importer expects the text encoders with their original key names, but the
# VAE with the standalone naming (decoder.conv_in.weight, ...).
PARTS = [
    ("clip_l", "conditioner.embedders.0.", False),
    ("clip_g", "conditioner.embedders.1.", False),
    ("vae", "first_stage_model.", True),
]

def main(path):
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        header = json.loads(f.read(n))
        base = 8 + n
        meta = header.pop("__metadata__", None)
        for name, prefix, strip in PARTS:
            keys = sorted(k for k in header if k.startswith(prefix))
            if not keys:
                print(f"{name}: no tensors with prefix {prefix!r}, skipped")
                continue
            out_header, blobs, offset = {}, [], 0
            for k in keys:
                info = header[k]
                start, end = info["data_offsets"]
                size = end - start
                out_key = k[len(prefix):] if strip else k
                out_header[out_key] = {"dtype": info["dtype"], "shape": info["shape"],
                                       "data_offsets": [offset, offset + size]}
                blobs.append((base + start, size))
                offset += size
            hb = json.dumps(out_header, separators=(",", ":")).encode()
            hb += b" " * ((8 - len(hb) % 8) % 8)
            out = os.path.join(os.path.dirname(os.path.abspath(path)), f"{name}.safetensors")
            with open(out, "wb") as o:
                o.write(struct.pack("<Q", len(hb))); o.write(hb)
                for start, size in blobs:
                    f.seek(start)
                    remaining = size
                    while remaining:
                        chunk = f.read(min(remaining, 64 << 20))
                        o.write(chunk); remaining -= len(chunk)
            print(f"{name}: {len(keys)} tensors -> {out} ({os.path.getsize(out)} bytes)")

if __name__ == "__main__":
    main(sys.argv[1])
