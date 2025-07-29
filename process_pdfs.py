import os
import json
import fitz  # PyMuPDF
import re

class PDFOutlineExtractor:
    def __init__(self):
        pass

    def clean_text(self, text):
        text = text.strip()
        if not text or len(text) <= 2:
            return ""
        if re.fullmatch(r"[0-9.\-]+", text):  # numbers or versions
            return ""
        if re.fullmatch(r"[. \-]{5,}", text):  # dotted lines or visual separators
            return ""
        if text.lower().startswith("copyright") or "page" in text.lower():
            return ""
        if text.isupper() and len(text) <= 4:  # avoid acronyms like "PDF"
            return ""
        return text

    def extract_text_blocks(self, pdf_path):
        doc = fitz.open(pdf_path)
        blocks = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_blocks = page.get_text("dict")["blocks"]
            for block in page_blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = self.clean_text(span["text"])
                            if not text:
                                continue
                            blocks.append({
                                "text": text,
                                "page": page_num + 1,
                                "font": span["font"],
                                "size": round(span["size"], 1),
                                "flags": span["flags"],
                                "bbox": span["bbox"]
                            })
        return blocks

    def build_font_ranking(self, blocks):
        sizes = {}
        for b in blocks:
            sizes[b["size"]] = sizes.get(b["size"], 0) + 1
        ranked = sorted(sizes.items(), key=lambda x: (-x[0], -x[1]))  # larger fonts first
        return [s for s, _ in ranked]

    def detect_title(self, blocks, largest_font_size):
        title_candidates = [b for b in blocks if b["page"] == 1 and b["size"] == largest_font_size]
        title_texts = [b["text"] for b in title_candidates if len(b["text"].split()) > 2]
        return " ".join(title_texts).strip() if title_texts else "Untitled"

    def classify_blocks(self, blocks, size_order):
        size_rank = {sz: i for i, sz in enumerate(size_order)}
        outline = []
        seen = set()
        for b in blocks:
            text = b["text"]
            if text in seen:
                continue
            seen.add(text)
            rank = size_rank.get(b["size"], 100)
            if rank == 0:
                level = "H1"
            elif rank == 1:
                level = "H2"
            elif rank == 2:
                level = "H3"
            else:
                continue  # Ignore small size "content"
            if len(text) > 100 or len(text.split()) > 20:
                continue  # likely paragraph text
            outline.append({
                "level": level,
                "text": text,
                "page": b["page"]
            })
        return outline

    def process_pdf(self, pdf_path):
        blocks = self.extract_text_blocks(pdf_path)
        if not blocks:
            return {}

        size_order = self.build_font_ranking(blocks)
        title = self.detect_title(blocks, size_order[0])
        outline = self.classify_blocks(blocks, size_order)

        return {
            "title": title,
            "outline": outline
        }


def batch_process():
    input_dir = "files"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    extractor = PDFOutlineExtractor()
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]

    for fname in pdf_files:
        input_path = os.path.join(input_dir, fname)
        output_path = os.path.join(output_dir, os.path.splitext(fname)[0] + ".json")

        try:
            result = extractor.process_pdf(input_path)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"✅ Processed {fname}")
        except Exception as e:
            print(f"❌ Failed {fname} -> {e}")

if __name__ == "__main__":
    batch_process()
