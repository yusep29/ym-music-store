import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .preprocessing import preprocess


class MusicChatbot:
    """Chatbot FAQ berbasis TF-IDF dengan pencarian katalog produk langsung."""

    CATEGORY_MAP = {
        "gitar": "Guitars", "gitar elektrik": "Guitars", "gitar akustik": "Guitars",
        "guitars": "Guitars", "electric guitar": "Guitars", "acoustic guitar": "Guitars",
        "bass": "Bass", "gitar bass": "Bass", "bass elektrik": "Bass",
        "drum": "Drums", "drums": "Drums", "drum elektrik": "Drums", "drum akustik": "Drums",
        "keyboard": "Keyboards", "keyboard musik": "Keyboards", "piano": "Keyboards",
        "piano digital": "Keyboards", "ampli": "Amps", "amplifier": "Amps", "amp": "Amps",
        "efek": "Accessories", "pedal": "Accessories", "aksesoris": "Accessories",
        "aksesori": "Accessories", "accessories": "Accessories"
    }

    def __init__(self, kb_path, products_path):
        self.kb_path = kb_path
        self.products_path = products_path
        self.reload()

    def reload(self):
        with open(self.kb_path, "r", encoding="utf-8") as f:
            self.knowledge = json.load(f)
        with open(self.products_path, "r", encoding="utf-8") as f:
            self.products = json.load(f)
        self.questions = [preprocess(" ".join(item["patterns"])) for item in self.knowledge]
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform(self.questions) if self.questions else None

    @staticmethod
    def _normalise(text):
        text = str(text or "").lower()
        text = re.sub(r"[^a-z0-9]+", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def product_cards(self, category=None, limit=3):
        matches = [p for p in self.products if not category or p.get("category", "").lower() == category.lower()]
        return matches[:limit]

    def _category_from_message(self, message):
        text = self._normalise(message)
        # Cek frasa yang lebih panjang terlebih dahulu agar 'gitar bass' tidak dianggap gitar.
        for keyword in sorted(self.CATEGORY_MAP, key=len, reverse=True):
            if re.search(r"\b" + re.escape(keyword) + r"\b", text):
                return self.CATEGORY_MAP[keyword]
        return None

    def _find_named_products(self, message):
        text = self._normalise(message)
        matches = []
        for product in self.products:
            terms = [product.get("name", "")] + product.get("aliases", [])
            normalised_terms = [self._normalise(term) for term in terms if term]
            found = [term for term in normalised_terms if term and re.search(r"\b" + re.escape(term) + r"\b", text)]
            if found:
                # Prioritaskan kecocokan nama/alias paling spesifik.
                matches.append((max(found, key=len), product))
        matches.sort(key=lambda item: len(item[0]), reverse=True)
        result = []
        seen = set()
        for _, product in matches:
            if product.get("id") not in seen:
                result.append(product)
                seen.add(product.get("id"))
        return result

    @staticmethod
    def _format_price(price):
        try:
            return "Rp" + f"{int(price):,}".replace(",", ".")
        except (TypeError, ValueError):
            return "Harga hubungi admin"

    def _format_product_detail(self, product):
        lines = [
            f"{product.get('name', 'Produk')} — {self._format_price(product.get('price'))}",
            f"Kategori: {product.get('category', '-')}",
            f"Stok: {product.get('stock', 'Belum diinformasikan')} unit",
            product.get("description", "")
        ]
        specs = product.get("specifications") or {}
        if specs:
            lines.append("Spesifikasi:")
            lines.extend([f"• {key}: {value}" for key, value in specs.items()])
        if product.get("ideal_for"):
            lines.append(f"Cocok untuk: {product['ideal_for']}")
        return "\n".join(line for line in lines if line)

    def _product_response(self, message):
        text = self._normalise(message)
        named_products = self._find_named_products(message)
        category = self._category_from_message(message)

        compare_words = ("bandingkan", "dibanding", "perbedaan", "beda", "compare", "lebih bagus")
        if len(named_products) >= 2 and any(word in text for word in compare_words):
            first, second = named_products[:2]
            answer = (
                f"Berikut perbandingan {first['name']} dan {second['name']}:\n\n"
                f"{self._format_product_detail(first)}\n\n"
                f"{self._format_product_detail(second)}\n\n"
                "Pilihan terbaik bergantung pada kebutuhan, karakter suara, dan anggaranmu."
            )
            return {"answer": answer, "confidence": 1.0, "products": [first, second]}

        if named_products:
            product = named_products[0]
            if any(word in text for word in ("harga", "berapa", "banderol", "biaya")):
                answer = f"Harga {product['name']} adalah {self._format_price(product.get('price'))}."
            elif any(word in text for word in ("stok", "tersedia", "ready", "masih ada")):
                answer = f"{product['name']} tercatat memiliki stok {product.get('stock', 0)} unit. Silakan konfirmasi stok aktual kepada admin toko."
            else:
                answer = self._format_product_detail(product)
            return {"answer": answer, "confidence": 1.0, "products": [product]}

        browse_words = ("apa saja", "tersedia", "jual", "daftar", "pilihan", "rekomendasi", "punya", "katalog", "produk", "ada ")
        if category and any(word in text for word in browse_words):
            items = self.product_cards(category, limit=20)
            if not items:
                return {"answer": f"Maaf, belum ada produk kategori {category} di katalog.", "confidence": 1.0, "products": []}
            lines = [f"Berikut produk kategori {category} yang ada di katalog:"]
            lines.extend([f"{i}. {p['name']} — {self._format_price(p.get('price'))} (stok: {p.get('stock', 0)})\n   {p.get('description', '')}" for i, p in enumerate(items, 1)])
            lines.append("\nSebutkan nama produk jika ingin melihat spesifikasi lengkapnya.")
            return {"answer": "\n".join(lines), "confidence": 1.0, "products": items[:6]}

        return None

    def reply(self, message):
        text = preprocess(message)
        if not text:
            return {"answer": "Boleh ceritakan sedikit lebih detail? Aku siap membantu menemukan instrumen yang cocok.", "confidence": 0, "products": []}

        # Pencarian katalog didahulukan agar pertanyaan nama produk tidak tertangkap FAQ umum.
        product_result = self._product_response(message)
        if product_result:
            return product_result

        if self.matrix is None:
            return {"answer": "Maaf, basis pengetahuan chatbot belum tersedia.", "confidence": 0, "products": []}

        query_vec = self.vectorizer.transform([text])
        scores = cosine_similarity(query_vec, self.matrix).flatten()
        best_idx = int(scores.argmax())
        confidence = float(scores[best_idx])

        if confidence < 0.12:
            answer = ("Maaf, aku belum menemukan jawaban yang benar-benar sesuai. "
                      "Coba tanyakan tentang produk, spesifikasi, harga, stok, rekomendasi instrumen, "
                      "pengiriman, pembayaran, atau informasi toko.")
            return {"answer": answer, "confidence": round(confidence, 3), "products": []}

        item = self.knowledge[best_idx]
        answer = item["answer"]
        category = self._category_from_message(message)
        products = self.product_cards(category, 3) if category else []
        return {"answer": answer, "confidence": round(confidence, 3), "products": products}
