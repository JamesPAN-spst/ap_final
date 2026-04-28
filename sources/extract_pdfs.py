"""Extract PDFs under sources/pdf into sources/text.

Large handouts can be split into multiple text chunks.
"""

from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parent
PDF_DIR = ROOT / 'pdf'
OUT_DIR = ROOT / 'text'
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Files & desired chunking (None = single file)
SPLIT = {
    '3-types.pdf': 25,
}


def extract(pdf_path: Path, chunk_pages=None):
    doc = fitz.open(pdf_path)
    page_count = doc.page_count
    base = pdf_path.stem
    if chunk_pages is None or page_count <= chunk_pages:
        text = '\n\n'.join(
            f'\n===== PAGE {index + 1}/{page_count} =====\n' + doc[index].get_text('text')
            for index in range(page_count)
        )
        (OUT_DIR / f'{base}.txt').write_text(text, encoding='utf-8')
        print(f'[OK] {base}.txt  ({page_count} pages)')
        return

    part = 1
    for start in range(0, page_count, chunk_pages):
        end = min(start + chunk_pages, page_count)
        text = f'# {base} -- part {part}  pages {start + 1}-{end} / {page_count}\n\n'
        text += '\n\n'.join(
            f'\n===== PAGE {index + 1}/{page_count} =====\n' + doc[index].get_text('text')
            for index in range(start, end)
        )
        (OUT_DIR / f'{base}__part{part}.txt').write_text(text, encoding='utf-8')
        print(f'[OK] {base}__part{part}.txt  (pages {start + 1}-{end})')
        part += 1


def main():
    for pdf_path in sorted(PDF_DIR.glob('*.pdf')):
        extract(pdf_path, SPLIT.get(pdf_path.name))

    print('\nFiles produced:')
    for text_path in sorted(OUT_DIR.glob('*.txt')):
        print(f'  {text_path.name}  ({text_path.stat().st_size // 1024} KB)')


if __name__ == '__main__':
    main()