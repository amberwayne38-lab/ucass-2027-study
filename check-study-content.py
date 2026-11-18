"""Run from any working directory before publishing a study-content change."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent
BATCH = re.compile(r'印刷页|(?:PDF|教材|原书)?第\s*\d+(?:\s*[—–至-]\s*\d+)?\s*页|(?<!\w)p\.\s*\d+|^p\s*\d+$|第[一二三四五六七八九十\d]+批|处理批次', re.I)


class Titles(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = None
        self.parts = []
        self.values = []

    def handle_starttag(self, tag, attrs):
        if self.active is None and tag in {'title','h1','h2','h3','h4','h5','h6','a','summary'}:
            self.active = tag
            self.parts = []

    def handle_endtag(self, tag):
        if tag == self.active:
            self.values.append(''.join(self.parts))
            self.active = None

    def handle_data(self, data):
        if self.active:
            self.parts.append(data)


def check():
    errors = []
    for file in ROOT.glob('*.html'):
        parser = Titles()
        parser.feed(file.read_text())
        for title in parser.values:
            if BATCH.search(title):
                errors.append(f'{file.name}: {title}')
    points = json.loads((ROOT/'politics-chapters.js').read_text().split('=',1)[1].strip().removesuffix(';'))
    for field in ('id','question','recall'):
        if len({p[field] for p in points}) != len(points):
            errors.append(f'Duplicate politics {field}')
    for point in points:
        if not point['source'] or len(set(point['options'])) != 4 or point['options'].count(point['answer']) != 1:
            errors.append(point['id'])
        multi = point.get('multiple')
        if multi:
            options, keys = multi['options'], multi['correct']
            if len(options) != 4 or len(set(options)) != 4 or not (2 <= len(keys) < 4) or keys != sorted(set(keys)) or any(k not in range(4) for k in keys) or not multi['explanation']:
                errors.append(f'Invalid multi-select: {point["id"]}')
    all_prompts = [p['question'] for p in points] + [p['multiple']['prompt'] for p in points if p.get('multiple')]
    if len(set(all_prompts)) != len(all_prompts):
        errors.append('Duplicate politics choice prompt')
    if errors:
        raise SystemExit('\n'.join(errors))


if __name__ == '__main__':
    check()
