# SmartCV Analyzer

> AI-powered CV analyzer that scores your resume against job descriptions, identifies gaps, and gives specific improvement suggestions — in seconds.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?style=flat-square&logo=streamlit)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ✨ Features

| Feature | Description |
|---|---|
| **Match Score** | Persentase kecocokan CV dengan job description (0–100%) |
| **Gap Analysis** | Analisis per section: Skills, Experience, Education, Soft Skills, Keywords |
| **AI Suggestions** | Saran perbaikan spesifik dengan prioritas (tinggi/sedang/rendah) |
| **Keyword Matching** | Deteksi keyword JD yang ada/hilang di CV |
| **Multi JD Compare** | Bandingkan 1 CV dengan 3 job description sekaligus |
| **PDF Export** | Download laporan lengkap dalam format PDF |

---

## Demo

**Live App:** [smartcv-analyzer.streamlit.app](https://smartcv-analyzer.streamlit.app) *(deploy setelah setup)*

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **AI Engine:** Groq API + LLaMA 3.3 70B Versatile
- **PDF Reading:** PyMuPDF (fitz)
- **PDF Export:** ReportLab
- **Language:** Python 3.10+

---

## ⚡ Quick Start

### 1. Clone repository

```bash
git clone https://github.com/username/smartcv-analyzer.git
cd smartcv-analyzer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup API Key

Buat file `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxx"
```

> Dapatkan Groq API key gratis di [console.groq.com](https://console.groq.com)

### 4. Jalankan aplikasi

```bash
streamlit run app.py
```

Buka browser → `http://localhost:8501`

---

## 📁 Project Structure

```
smartcv-analyzer/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Dependencies
├── README.md
├── .streamlit/
│   └── secrets.toml        # API keys (jangan di-commit!)
└── utils/
    ├── __init__.py
    ├── pdf_reader.py       # PDF text extraction (PyMuPDF)
    ├── analyzer.py         # AI analysis via Groq API
    └── exporter.py         # PDF report generation (ReportLab)
```

---

## ☁️ Deploy ke Streamlit Cloud

1. Push project ke GitHub
2. Buka [share.streamlit.io](https://share.streamlit.io)
3. Connect repository → pilih `app.py`
4. Di **Secrets**, tambahkan:
   ```
   GROQ_API_KEY = "gsk_xxxx"
   ```
5. Deploy → selesai!

---

## 🔒 .gitignore

Pastikan file ini ada di `.gitignore`:

```
.streamlit/secrets.toml
__pycache__/
*.pyc
.env
```

---

## 📸 Screenshots

<img width="601" height="461" alt="smartcv-analyzer2" src="https://github.com/user-attachments/assets/74f8d881-475c-44b8-bfb7-28f3712fd6ed" />


---

##  Contributing

Pull requests welcome! Feel free to open issues untuk bug reports atau feature requests.

---

## 📄 License

MIT License — bebas digunakan dan dimodifikasi.

---

*Built with using Groq + LLaMA 3.3 + Streamlit*
