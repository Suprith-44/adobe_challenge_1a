# adobe_challenge_1a

This solution extracts structured outline information from PDF files using PyMuPDF (fitz) and summarizes it into a clean, structured JSON format. It detects the main document title and organizes the content into hierarchical headings (H1, H2, H3) based on font size and layout cues.

Instead of relying on large language models (LLMs) — which often exceed memory constraints (200MB) and can compromise performance — our approach uses a combination of regex patterns and rule-based heuristics for title and heading detection. This makes our solution lightweight, extremely fast, and highly accurate, even on resource-constrained systems.

Library Used
PyMuPDF (fitz): For reading and parsing PDF content, including layout, font size, and position data to support our custom heading classification logic.

Instructions to run

1. clone the repo
2. make sure docker is installed by running <br><code> docker </code>
3. then from root dir of the project run <br><code> docker build -t pdf-outline-extractor . </code>
4. after the image is built run <br><code> docker run --rm -v "$(pwd)/output:/app/output" pdf-outline-extractor </code>
