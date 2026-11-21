# YM Music Store

Aplikasi demo toko alat musik daring dengan chatbot berbasis pencarian (retrieval-based) berbahasa Indonesia.

## Fitur
- Halaman utama responsif dan katalog produk
- Filter kategori dan pencarian produk
- Chatbot dengan animasi equalizer saat menyiapkan jawaban
- REST API menggunakan Flask
- Mesin chatbot menggunakan TF-IDF dan Cosine Similarity
- Prapemrosesan teks Bahasa Indonesia dengan Sastrawi
- Rekomendasi produk berdasarkan kategori
- Halaman admin sederhana untuk mengelola basis pengetahuan chatbot

## Persyaratan
- Python 3.10 atau lebih baru
- Browser web modern

## Menjalankan backend

Buka terminal:

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Pasang pustaka dan jalankan Flask:

```bash
pip install -r requirements.txt
python app.py
```

Backend berjalan di `http://127.0.0.1:5000`.

## Menjalankan frontend

Buka terminal kedua dari folder utama project:

```bash
cd frontend
python -m http.server 5500
```

Buka `http://127.0.0.1:5500`.

Halaman admin: `http://127.0.0.1:5500/admin.html`.

## Alur kerja chatbot
1. Pengguna mengirim pertanyaan dari antarmuka.
2. Frontend mengirim permintaan ke `POST /api/chat`.
3. Backend melakukan prapemrosesan teks Bahasa Indonesia.
4. TF-IDF mengubah pola pertanyaan dalam basis pengetahuan menjadi vektor.
5. Cosine Similarity memilih pola pertanyaan yang paling mirip.
6. Jika skor kemiripan di bawah ambang batas, chatbot memberikan jawaban cadangan.
7. Frontend menampilkan jawaban dan rekomendasi produk jika tersedia.

## Endpoint API
- `GET /api/health`
- `GET /api/products`
- `GET /api/categories`
- `POST /api/chat` dengan isi `{"message":"..."}` 
- `GET /api/admin/knowledge`
- `PUT /api/admin/knowledge`
- `GET /api/admin/stats`

## Catatan
- Nama produk, harga, stok, kontak, dan informasi pembayaran merupakan data demonstrasi.
- Prototipe ini belum menyediakan checkout atau pembayaran sungguhan.
- Endpoint admin belum menggunakan autentikasi dan hanya ditujukan untuk demonstrasi lokal. Tambahkan autentikasi dan validasi sebelum aplikasi dipublikasikan.
- Rekomendasi produk saat ini menggunakan pencocokan kategori sederhana, bukan model rekomendasi terlatih.
