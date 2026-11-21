
const API = "http://127.0.0.1:5000/api";
const grid = document.getElementById("productGrid");
const money = n => new Intl.NumberFormat("id-ID",{style:"currency",currency:"IDR",maximumFractionDigits:0}).format(n);

async function loadProducts(category="All", query="") {
  grid.innerHTML = '<div class="loading-products">Sedang menyiapkan katalog...</div>';
  try {
    const params = new URLSearchParams();
    if(category && category!=="All") params.set("category",category);
    if(query) params.set("q",query);
    const res = await fetch(`${API}/products?${params}`);
    if(!res.ok) throw new Error("API unavailable");
    const products = await res.json();
    if(!products.length){grid.innerHTML='<div class="loading-products">Produk tidak ditemukan. Coba kata kunci lain.</div>';return;}
    grid.innerHTML = products.map(p=>`
      <article class="product-card"
        data-product-id="${p.id}"
        data-product-name="${p.name}">
          <div class="product-art"><span class="product-tag">${p.tag}</span><span class="product-emoji">${p.emoji}</span></div>
          <div class="product-info"><span class="product-category">${p.category}</span><h3>${p.name}</h3>
          <p>${p.description}</p><div class="product-bottom"><span class="price">${money(p.price)}</span><button onclick="askAbout('${p.name.replace(/'/g,"\\'")}')">Ask assistant ↗</button></div>
          <div class="stock" style="margin-top:9px">${p.stock>0?`● ${p.stock} unit tersedia`:"● Stok habis"}</div></div>
      </article>`).join("");
  } catch(e) {grid.innerHTML='<div class="loading-products">Tidak dapat terhubung ke server toko. Jalankan backend Flask terlebih dahulu.</div>';}
}
let activeCategory="All";
document.querySelectorAll(".filter").forEach(btn=>btn.addEventListener("click",()=>{
  document.querySelectorAll(".filter").forEach(b=>b.classList.remove("active"));
  btn.classList.add("active");activeCategory=btn.dataset.category;loadProducts(activeCategory,document.getElementById("productSearch").value);
}));
document.querySelectorAll(".category-card").forEach(btn=>btn.addEventListener("click",()=>{
  activeCategory=btn.dataset.category;
  document.querySelectorAll(".filter").forEach(b=>b.classList.toggle("active",b.dataset.category===activeCategory));
  loadProducts(activeCategory);document.getElementById("products").scrollIntoView({behavior:"smooth"});
}));
let searchTimer;
document.getElementById("productSearch").addEventListener("input",e=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>loadProducts(activeCategory,e.target.value),250);});

const panel=document.getElementById("chatPanel"), body=document.getElementById("chatBody"), input=document.getElementById("chatInput");
// Klik rekomendasi produk dari chatbot
body.addEventListener("click", event => {
    const product = event.target.closest(".reply-product");

    if (product) {
        openProductInCatalog(product);
    }
});

// Dukungan keyboard Enter dan Space
body.addEventListener("keydown", event => {
    if (event.key !== "Enter" && event.key !== " ") return;

    const product = event.target.closest(".reply-product");

    if (product) {
        event.preventDefault();
        openProductInCatalog(product);
    }
});
function openChat(){panel.classList.add("open");document.getElementById("chatLauncher").style.display="none";setTimeout(()=>input.focus(),200)}
function closeChat(){panel.classList.remove("open");document.getElementById("chatLauncher").style.display="flex"}
async function openProductInCatalog(recommendation) {
    const productId = recommendation.dataset.productId;
    const productName = recommendation.dataset.productName;

    // Tutup chatbot
    closeChat();

    // Reset filter dan pencarian
    activeCategory = "All";

    document.querySelectorAll(".filter").forEach(btn => {
        btn.classList.toggle(
            "active",
            btn.dataset.category === "All"
        );
    });

    const searchInput = document.getElementById("productSearch");
    searchInput.value = "";

    // Muat ulang katalog
    await loadProducts("All", "");

    // Cari produk berdasarkan ID atau nama
    const productCard = Array.from(
        grid.querySelectorAll(".product-card")
    ).find(card =>
        (productId && card.dataset.productId === productId) ||
        (productName && card.dataset.productName === productName)
    );

    if (!productCard) return;

    // Scroll menuju produk
    productCard.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

    // Berikan efek highlight
    productCard.classList.remove("product-highlighted");

    void productCard.offsetWidth;

    productCard.classList.add("product-highlighted");

    setTimeout(() => {
        productCard.classList.remove("product-highlighted");
    }, 2300);
}
async function openProductInCatalog(recommendation) {
    const productId = recommendation.dataset.productId;
    const productName = recommendation.dataset.productName;

    // Tutup chatbot
    closeChat();

    // Reset filter dan pencarian
    activeCategory = "All";

    document.querySelectorAll(".filter").forEach(btn => {
        btn.classList.toggle(
            "active",
            btn.dataset.category === "All"
        );
    });

    const searchInput = document.getElementById("productSearch");
    searchInput.value = "";

    // Muat ulang katalog
    await loadProducts("All", "");

    // Cari produk berdasarkan ID atau nama
    const productCard = Array.from(
        grid.querySelectorAll(".product-card")
    ).find(card =>
        (productId && card.dataset.productId === productId) ||
        (productName && card.dataset.productName === productName)
    );

    if (!productCard) return;

    // Scroll menuju produk
    productCard.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

    // Berikan efek highlight
    productCard.classList.remove("product-highlighted");

    void productCard.offsetWidth;

    productCard.classList.add("product-highlighted");

    setTimeout(() => {
        productCard.classList.remove("product-highlighted");
    }, 2300);
}
document.getElementById("chatLauncher").onclick=openChat;document.getElementById("closeChat").onclick=closeChat;
document.getElementById("heroChat").onclick=openChat;document.getElementById("bannerChat").onclick=openChat;
document.querySelectorAll(".quick-prompts button").forEach(b=>b.onclick=()=>sendMessage(b.dataset.prompt));
function addMessage(text,who="bot",products=[]){
  const row=document.createElement("div");row.className=`message-row ${who==="user"?"user-row":"bot-row"}`;
  if(who==="bot"){const av=document.createElement("div");av.className="mini-avatar";av.textContent="♫";row.appendChild(av);}
  const content=document.createElement("div");content.className="message-content";
  const bubble=document.createElement("div");bubble.className="bubble";bubble.textContent=text;content.appendChild(bubble);
  if (products.length) {
      const cards = document.createElement("div");
      cards.className = "reply-products";

      cards.innerHTML = products.map(p => `
          <div class="reply-product"
              data-product-id="${p.id ?? ""}"
              data-product-name="${p.name}"
              role="button"
              tabindex="0"
              aria-label="Lihat ${p.name} di katalog">

              <span>${p.emoji || "🎵"}</span>

              <div>
                  <b>${p.name}</b>
                  <small>${money(p.price)}</small>
              </div>

          </div>
      `).join("");

      content.appendChild(cards);
  }
  const time=document.createElement("span");time.className="message-time";time.textContent=who==="user"?"Kamu · baru saja":"Asisten YM · baru saja";content.appendChild(time);row.appendChild(content);body.appendChild(row);body.scrollTop=body.scrollHeight;
}
function showTyping(){
  const row=document.createElement("div");row.className="typing-row";row.id="typingIndicator";
  row.innerHTML='<div class="equalizer"><i></i><i></i><i></i><i></i><i></i></div><span class="typing-label">Sedang mencari instrumen yang cocok...</span>';
  body.appendChild(row);body.scrollTop=body.scrollHeight;return row;
}
async function sendMessage(text){
  text=(text||input.value).trim();if(!text)return;
  addMessage(text,"user");input.value="";input.style.height="auto";

  // Tampilkan equalizer dan beri waktu browser untuk merender animasinya.
  const typing=showTyping();
  const typingStartedAt=Date.now();
  await new Promise(resolve=>setTimeout(resolve,50));

  try{
    const res=await fetch(`${API}/chat`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:text})});
    if(!res.ok)throw new Error("API error");
    const data=await res.json();

    // Jaga agar animasi terlihat minimal 650 ms, termasuk saat API sangat cepat.
    const remainingTime=2000-(Date.now()-typingStartedAt);
    if(remainingTime>0)await new Promise(resolve=>setTimeout(resolve,remainingTime));

    typing.remove();
    addMessage(data.answer,"bot",data.products||[]);
  }catch(e){
    const remainingTime=650-(Date.now()-typingStartedAt);
    if(remainingTime>0)await new Promise(resolve=>setTimeout(resolve,remainingTime));
    typing.remove();
    addMessage("Maaf, aku belum bisa terhubung ke server. Pastikan backend Flask sedang berjalan, lalu coba lagi, ya.","bot");
  }
}
document.getElementById("sendChat").onclick=()=>sendMessage();
input.addEventListener("keydown",e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();sendMessage();}});
input.addEventListener("input",()=>{input.style.height="auto";input.style.height=Math.min(input.scrollHeight,75)+"px";});
window.askAbout=name=>{openChat();sendMessage(`Ceritakan tentang ${name}`)};
document.getElementById("menuToggle").onclick=()=>document.querySelector(".navbar nav").classList.toggle("show");
loadProducts();
