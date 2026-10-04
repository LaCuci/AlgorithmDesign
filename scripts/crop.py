#!/usr/bin/env python3
"""Extract a source region from the PNGs produced by extract.swift (requires Pillow)."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('lecture')
parser.add_argument('page', type=int)
parser.add_argument('name')
parser.add_argument('box', help='Normalized left,top,right,bottom coordinates')
parser.add_argument('--kind', choices=['diagram', 'unreadable'], default='diagram')
parser.add_argument('--note', default='')
parser.add_argument('--exclude', action='append', default=[], help='Normalized rectangle of adjacent non-diagram content transcribed separately')
args = parser.parse_args()
box = [float(v) for v in args.box.split(',')]
if len(box) != 4 or not (0 <= box[0] < box[2] <= 1 and 0 <= box[1] < box[3] <= 1):
    parser.error('Invalid crop coordinates')
root = Path(__file__).resolve().parents[1]
source = root / f'build/extraction/{args.lecture}-{args.page:03}.png'
relative = f'assets/{args.lecture}/page-{args.page:03}-{args.name}.png'
target = root / relative
target.parent.mkdir(parents=True, exist_ok=True)
with Image.open(source) as im:
    pixels = [round(box[i] * (im.width if i % 2 == 0 else im.height)) for i in range(4)]
    for rectangle in args.exclude:
        values = [float(v) for v in rectangle.split(',')]
        if len(values) != 4 or not (0 <= values[0] < values[2] <= 1 and 0 <= values[1] < values[3] <= 1):
            parser.error('Invalid exclusion rectangle')
        area = [round(values[i] * (im.width if i % 2 == 0 else im.height)) for i in range(4)]
        ImageDraw.Draw(im).rectangle(area, fill='white')
    im.crop(pixels).save(target)
record_path = root / 'build/extraction/crops.json'
records = json.loads(record_path.read_text()) if record_path.exists() else []
records = [r for r in records if r['path'] != relative]
records.append(dict(lecture=args.lecture, page=args.page, path=relative, kind=args.kind,
                    normalized_box=box, excluded_adjacent_regions=args.exclude, note=args.note))
record_path.write_text(json.dumps(records, indent=2) + '\n')
print(relative)
