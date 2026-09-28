#!/usr/bin/env python3
"""Pull the Brand Feeds Google Sheet and rewrite data/feed-data.js for this fork.

    python3 tools/sync_sheet.py                 # pull the live sheet
    python3 tools/sync_sheet.py --file x.xlsx   # use a downloaded copy instead
    python3 tools/sync_sheet.py --check         # validate only, write nothing

Tabs come from tools/sheet.config.json; each tab is one independent feed variant.
Google Drive images are downloaded into assets/sheet/ so the feed never hotlinks Drive.
"""
import argparse, io, json, os, re, sys, urllib.request, datetime
from openpyxl import load_workbook
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sheet_schema import BRAND_KEYS, POSTS_MARKER, COL_KEYS

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'data', 'feed-data.js'); IMG_DIR = os.path.join(ROOT, 'assets', 'sheet')
STATUS = {'live', 'draft', 'hidden'}; LOCS = {'feed', 'deck', 'onboarding'}
TYPES = {'image', 'table', 'text', 'chart', 'rings', 'about', 'brandkit', 'connect'}
AGENTS = {'creative', 'performance', 'storefront', 'visibility', 'crm', 'orchestrator'}
errors, warnings = [], []

def s(v): return '' if v is None else str(v).strip()

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'feed-sync'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(), r.headers.get('Content-Type', '')

DRIVE_ID = re.compile(r'(?:/d/|[?&]id=)([A-Za-z0-9_-]{20,})')
def resolve_image(ref, where):
    """repo path -> as is; https -> as is; Drive link -> downloaded copy in assets/sheet/."""
    ref = ref.strip()
    if not ref: return None
    m = DRIVE_ID.search(ref) if 'drive.google.com' in ref or 'docs.google.com' in ref else None
    if m:
        fid = m.group(1)
        os.makedirs(IMG_DIR, exist_ok=True)
        hit = [f for f in os.listdir(IMG_DIR) if f.startswith(fid + '.')]
        if hit: return f'assets/sheet/{hit[0]}'
        try:
            data, ctype = fetch(f'https://drive.google.com/uc?export=download&id={fid}')
        except Exception as e:
            errors.append(f'{where}: could not download Drive image ({e})'); return None
        if 'text/html' in ctype:
            errors.append(f'{where}: Drive would not hand over the file. Set it to "Anyone with the link can view", '
                          'or put the image in the repo and use its path.'); return None
        ext = {'image/png': 'png', 'image/webp': 'webp', 'image/gif': 'gif', 'video/mp4': 'mp4'}.get(ctype.split(';')[0], 'jpg')
        open(os.path.join(IMG_DIR, f'{fid}.{ext}'), 'wb').write(data)
        return f'assets/sheet/{fid}.{ext}'
    if ref.startswith('http'): return ref
    if not os.path.exists(os.path.join(ROOT, ref)):
        errors.append(f'{where}: image not found in repo: {ref}')
    return ref

def split_lines(v): return [x.strip() for x in re.split(r'[\n]|,(?=\s*(?:assets/|https?://))', s(v)) if x.strip()]

def parse_tags(v):
    out = []
    for t in [x.strip() for x in s(v).split(',') if x.strip()]:
        m = re.match(r'^(.*?)\s+(#[0-9a-fA-F]{3,8})$', t)
        if t.startswith('+'): out.append({'t': t[1:].strip(), 'gap': True})
        elif m: out.append({'t': m.group(1), 'dot': m.group(2)})
        else: out.append(t)
    return out

def parse_tab(ws):
    tab = ws.title; brand = {}; label_to_key = {l.lower(): k for l, k, _ in BRAND_KEYS}
    rows = list(ws.iter_rows(values_only=True)); header_at = None
    for i, r in enumerate(rows):
        a = s(r[0] if r else '').lower()
        if a == POSTS_MARKER: header_at = i; break
        if a in label_to_key: brand[label_to_key[a]] = s(r[1] if len(r) > 1 else '')
    if header_at is None:
        errors.append(f'{tab}: no header row starting with "{POSTS_MARKER}"'); return None
    header = [s(h).lower() for h in rows[header_at]]
    col = {h: i for i, h in enumerate(header) if h}
    missing = [k for k in ('post_id', 'status', 'location', 'type', 'agent') if k not in col]
    if missing: errors.append(f'{tab}: header is missing {", ".join(missing)}'); return None
    if brand.get('logo'): brand['logo'] = resolve_image(brand['logo'], f'{tab} logo')
    brand['colors'] = [c.strip() for c in brand.get('colors', '').split(',') if c.strip()]
    try: brand['products'] = int(float(brand.get('products') or 0))
    except ValueError: warnings.append(f'{tab}: Product count is not a number')
    posts, seen = [], set()
    for n, r in enumerate(rows[header_at + 1:], start=header_at + 2):
        g = lambda k: s(r[col[k]]) if k in col and col[k] < len(r) else ''
        pid = g('post_id')
        if not pid and not any(s(x) for x in r): continue
        where = f'{tab} row {n} ({pid or "no id"})'
        if not pid: errors.append(f'{where}: missing post_id'); continue
        if pid in seen: errors.append(f'{where}: duplicate post_id'); continue
        seen.add(pid)
        status = g('status').lower() or 'live'
        if status not in STATUS: errors.append(f'{where}: status "{status}" is not live/draft/hidden'); continue
        if status != 'live': continue
        loc = [x.strip().lower() for x in g('location').split(',') if x.strip()]
        if 'both' in loc: loc = [x for x in loc if x != 'both'] + ['onboarding', 'feed']
        bad = [x for x in loc if x not in LOCS]
        if bad or not loc: errors.append(f'{where}: location must be feed, deck and/or onboarding'); continue
        typ = g('type').lower(); agent = g('agent').lower() or 'orchestrator'
        if typ not in TYPES: errors.append(f'{where}: unknown type "{typ}"'); continue
        if agent not in AGENTS: errors.append(f'{where}: unknown agent "{agent}"'); continue
        p = {'id': pid, 'loc': loc, 'agent': agent}
        if g('deck_column'):
            if g('deck_column').lower() not in {'catalog', 'creatives', 'ads', 'storefront', 'visibility'}:
                errors.append(f'{where}: unknown deck_column "{g("deck_column")}"')
            else: p['deckCol'] = g('deck_column').lower()
        for k, dst in (('time', 'time'), ('title', 'title'), ('description', 'sub'), ('campaign', 'campaign'),
                       ('image_ratio', 'ratio'), ('image_fit', 'fit'), ('fit_bg', 'fitBg')):
            if g(k): p[dst] = g(k)
        imgs = [x for x in (resolve_image(i, where) for i in split_lines(g('images'))) if x]
        if imgs: p['images'] = imgs
        if g('badge'): p['badge'] = [g('badge'), g('badge_tone') or 'info']
        if g('table_rows'):
            p['rows'] = [[a.strip(), b.strip()] for a, _, b in (l.partition('|') for l in s(r[col['table_rows']]).split('\n')) if a.strip()]
        if g('cta_label'):
            p['cta'] = {'label': g('cta_label')}
            if g('cta_icon'): p['cta']['logo'] = g('cta_icon')
            if g('cta_color'): p['cta']['brandColor'] = g('cta_color')
        if g('extra_json'):
            try: p.update(json.loads(g('extra_json')))
            except json.JSONDecodeError as e: errors.append(f'{where}: extra_json is not valid JSON ({e.msg})')
        if typ in ('about', 'brandkit', 'connect'):
            p['about'] = True
            if g('tags'): p['tags'] = parse_tags(g('tags'))
            if g('editable').lower() in ('yes', 'y', 'true', '1'): p['editable'] = True
        if typ == 'connect': p['connect'] = g('connect') or 'store'
        if typ == 'brandkit':
            p['title'] = p.get('title') or 'Brand guidelines'
            p['brandkit'] = {'logo': brand.get('logo'), 'colors': brand['colors'],
                             'type': {'sample': brand.get('type_sample') or brand.get('name', ''),
                                      'face': brand.get('type_face', ''), 'name': brand.get('type_name', '')}}
        if typ == 'image' and not imgs: errors.append(f'{where}: type image but no images')
        if typ == 'table' and 'rows' not in p: errors.append(f'{where}: type table but no table_rows')
        if typ in ('chart', 'rings') and typ not in p: errors.append(f'{where}: type {typ} needs its data in extra_json')
        if typ not in ('connect', 'brandkit') and not p.get('title'): warnings.append(f'{where}: no title')
        if len(p.get('sub', '')) > 240 and 'onboarding' not in loc: warnings.append(f'{where}: description is {len(p["sub"])} chars (aim for ~200)')
        p['type'] = typ
        posts.append(p)
    return {'tab': tab, 'brand': brand, 'posts': posts}

def summary(old, new):
    lines = []
    oldv = {v['tab']: {p['id']: p for p in v['posts']} for v in (old or {}).get('variants', [])}
    for v in new['variants']:
        o = oldv.get(v['tab'], {}); n = {p['id']: p for p in v['posts']}
        add = [i for i in n if i not in o]; gone = [i for i in o if i not in n]
        chg = [i for i in n if i in o and n[i] != o[i]]
        moved = [i for i in n if i in o] != [i for i in o if i in n]
        bits = [f'{len(n)} live posts']
        if add: bits.append('added ' + ', '.join(add))
        if gone: bits.append('removed/hidden ' + ', '.join(gone))
        if chg: bits.append('edited ' + ', '.join(chg))
        if moved: bits.append('order changed')
        if not (add or gone or chg or moved) and o: bits.append('no changes')
        lines.append(f'  {v["tab"]}: ' + '; '.join(bits))
    return '\n'.join(lines)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--file'); ap.add_argument('--check', action='store_true')
    a = ap.parse_args(); cfg = json.load(open(os.path.join(HERE, 'sheet.config.json')))
    if a.file: raw = open(a.file, 'rb').read(); source = a.file
    else:
        source = f'https://docs.google.com/spreadsheets/d/{cfg["sheet_id"]}'
        raw, ctype = fetch(source + '/export?format=xlsx')
        if 'spreadsheetml' not in ctype: sys.exit('Could not download the sheet (is link sharing on?)')
    wb = load_workbook(io.BytesIO(raw), data_only=True)
    variants = []
    for t in cfg['tabs']:
        if t not in wb.sheetnames: errors.append(f'tab "{t}" not found in the sheet'); continue
        v = parse_tab(wb[t])
        if v: variants.append(v)
    for w in warnings: print('  warning:', w)
    if errors:
        print('Sync stopped, nothing written. Fix these in the sheet:'); [print('  -', e) for e in errors]; sys.exit(1)
    data = {'syncedAt': datetime.datetime.now().isoformat(timespec='seconds'), 'source': source, 'variants': variants}
    old = None
    if os.path.exists(OUT):
        try: old = json.loads(open(OUT).read().split('=', 1)[1].rstrip().rstrip(';'))
        except Exception: pass
    print(summary(old, data))
    if a.check: print('Check only: nothing written.'); return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f:
        f.write('// Generated by tools/sync_sheet.py from the Brand Feeds sheet. Do not edit by hand.\n')
        f.write('window.FEED_DATA = ' + json.dumps(data, ensure_ascii=False, indent=1) + ';\n')
    print('Wrote data/feed-data.js')

if __name__ == '__main__': main()
