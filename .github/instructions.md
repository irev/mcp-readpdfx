Proyek: OCR PDF MCP untuk LM Studio
Tujuan: Membuat agen OCR PDF yang dapat diintegrasikan dengan LM Studio untuk mengekstrak teks dari file PDF, baik yang digital maupun hasil scan.
Framework: FastAPI
Endpoint utama: /analyze_pdf
Langkah kerja:
Terima path file PDF dari LM Studio.
Deteksi apakah PDF digital atau hasil scan.
Jika scan → convert ke image (per halaman) → OCR.
Jika digital → ekstraksi teks langsung via PyMuPDF.
Jalankan paralel OCR untuk halaman banyak.
Return JSON hasil analisis (per halaman).

ocr_pdf_mcp/
├── ocr_pdf_mcp/
│   ├── __init__.py
│   ├── main.py
│   ├── pdf_utils.py
│   ├── ocr_worker.py
│   ├── pdf_text_extractor.py
│   ├── config.py
│
├── tests/
│   ├── test_ocr_worker.py
│   └── test_pdf_utils.py
│
├── requirements.txt
├── README.md
└── .env
