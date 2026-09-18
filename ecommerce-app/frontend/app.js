'use strict';

// ── API base — nginx proxies /api/* → api-gateway:8080 ────────────────────
const API = '/api';

// ── App state ─────────────────────────────────────────────────────────────
let user = JSON.parse(localStorage.getItem('shopeasy_user') || 'null');
let cart = JSON.parse(localStorage.getItem('shopeasy_cart') || '[]');
let allProducts = [];
let notifPollTimer = null;

// ── Bootstrap ─────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  syncAuthUI();
  loadProducts();
  syncCartUI();
  if (user) startNotifPolling();
});

// ─────────────────────────────────────────────────────────────────────────
// NAVIGATION
// ─────────────────────────────────────────────────────────────────────────
function showPage(name, el) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.getElementById('page-' + name).classList.add('active');
  if (el) el.classList.add('active');

  if (name === 'orders')        loadOrders();
  if (name === 'notifications') loadNotifications();
}

// ─────────────────────────────────────────────────────────────────────────
// PRODUCTS
// ─────────────────────────────────────────────────────────────────────────
async function loadProducts(category) {
  const grid = document.getElementById('products-grid');
  // Show skeleton
  grid.innerHTML = Array(4).fill('<div class="skeleton-card"></div>').join('');

  try {
    const url = category ? `${API}/products?category=${encodeURIComponent(category)}` : `${API}/products`;
    const res  = await fetch(url);
    if (!res.ok) throw new Error('Failed to load products');
    allProducts = await res.json();
    renderProducts(allProducts);
    document.getElementById('stat-products').textContent = allProducts.length;
  } catch (e) {
    grid.innerHTML = `
      <div class="empty-state" style="grid-column:1/-1">
        <div class="empty-state-icon">😕</div>
        <h3>Could not load products</h3>
        <p>${e.message}</p>
        <button class="btn-primary" onclick="loadProducts()">Try again</button>
      </div>`;
  }
}

function renderProducts(products) {
  const grid = document.getElementById('products-grid');
  const count = document.getElementById('results-count');

  if (!products.length) {
    grid.innerHTML = `
      <div class="empty-state" style="grid-column:1/-1">
        <div class="empty-state-icon">🔍</div>
        <h3>No products found</h3>
        <p>Try a different category</p>
      </div>`;
    count.textContent = '';
    return;
  }

  count.textContent = `${products.length} product${products.length !== 1 ? 's' : ''}`;

  grid.innerHTML = products.map(p => {
    const stockPill = p.stock === 0
      ? ''
      : p.stock < 5
        ? `<span class="product-stock-pill low-stock">Only ${p.stock} left</span>`
        : `<span class="product-stock-pill in-stock">${p.stock} in stock</span>`;

    const imageHtml = p.imageUrl
      ? `<img class="product-img" src="${p.imageUrl}" alt="${esc(p.name)}"
              onerror="this.parentElement.innerHTML='<div class=\\'product-img-placeholder\\'>📦</div>'"/>`
      : `<div class="product-img-placeholder">📦</div>`;

    return `
      <div class="product-card">
        <div class="product-image-wrap">
          ${imageHtml}
          <span class="category-badge">${esc(p.category)}</span>
          ${p.stock === 0 ? '<div class="out-of-stock-overlay">OUT OF STOCK</div>' : ''}
        </div>
        <div class="product-body">
          <div class="product-name">${esc(p.name)}</div>
          <div class="product-desc">${esc(p.description)}</div>
          <div class="product-footer">
            <span class="product-price">$${p.price.toFixed(2)}</span>
            ${stockPill}
          </div>
          <button
            class="add-cart-btn"
            id="atc-${p.id}"
            onclick="addToCart('${p.id}','${esc(p.name)}',${p.price},'${p.imageUrl || ''}')"
            ${p.stock === 0 ? 'disabled' : ''}>
            ${p.stock === 0 ? 'Out of Stock' : '+ Add to Cart'}
          </button>
        </div>
      </div>`;
  }).join('');
}

function filterProducts(category, btn) {
  document.querySelectorAll('.filter-chip').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  loadProducts(category === 'all' ? null : category);
}

// ─────────────────────────────────────────────────────────────────────────
// CART
// ─────────────────────────────────────────────────────────────────────────
function addToCart(id, name, price, imageUrl) {
  const existing = cart.find(i => i.productId === id);
  if (existing) existing.quantity++;
  else cart.push({ productId: id, name, price, imageUrl, quantity: 1 });
  saveCart();
  syncCartUI();

  // Flash the button green briefly
  const btn = document.getElementById('atc-' + id);
  if (btn) {
    btn.classList.add('added');
    btn.textContent = '✓ Added!';
    setTimeout(() => {
      btn.classList.remove('added');
      btn.textContent = '+ Add to Cart';
    }, 1500);
  }
  showToast(`${name} added to cart`, 'success');
}

function syncCartUI() {
  const total = cart.reduce((s, i) => s + i.price * i.quantity, 0);
  const count = cart.reduce((s, i) => s + i.quantity, 0);

  // Header bubble
  const bubble = document.getElementById('cart-count');
  if (count > 0) { bubble.textContent = count; bubble.style.display = 'flex'; }
  else bubble.style.display = 'none';

  document.getElementById('cart-subtitle').textContent = `${count} item${count !== 1 ? 's' : ''}`;

  // Cart body
  const body = document.getElementById('cart-body');
  const foot = document.getElementById('cart-foot');

  if (!cart.length) {
    body.innerHTML = `
      <div class="empty-drawer">
        <div class="empty-icon">🛒</div>
        <p>Your cart is empty</p>
        <span>Add some products to get started</span>
      </div>`;
    foot.style.display = 'none';
    return;
  }

  foot.style.display = 'block';
  document.getElementById('cart-subtotal').textContent = `$${total.toFixed(2)}`;
  document.getElementById('cart-shipping').textContent = total >= 99 ? 'Free' : '$9.99';
  document.getElementById('cart-total').textContent =
    total >= 99 ? `$${total.toFixed(2)}` : `$${(total + 9.99).toFixed(2)}`;

  body.innerHTML = cart.map((item, idx) => `
    <div class="cart-item">
      <div class="cart-item-thumb">
        ${item.imageUrl
          ? `<img src="${item.imageUrl}" alt="${esc(item.name)}"
                  onerror="this.parentElement.innerHTML='📦'">`
          : '📦'}
      </div>
      <div class="cart-item-info">
        <div class="cart-item-name">${esc(item.name)}</div>
        <div class="cart-item-price">$${(item.price * item.quantity).toFixed(2)}</div>
        <div class="qty-controls">
          <button class="qty-btn" onclick="changeQty(${idx},-1)">−</button>
          <span class="qty-num">${item.quantity}</span>
          <button class="qty-btn" onclick="changeQty(${idx},1)">+</button>
          <button class="remove-item" onclick="removeItem(${idx})">✕ Remove</button>
        </div>
      </div>
    </div>`).join('');
}

function changeQty(idx, delta) {
  cart[idx].quantity += delta;
  if (cart[idx].quantity <= 0) cart.splice(idx, 1);
  saveCart(); syncCartUI();
}
function removeItem(idx) {
  const name = cart[idx].name;
  cart.splice(idx, 1);
  saveCart(); syncCartUI();
  showToast(`${name} removed`, 'info');
}
function saveCart() { localStorage.setItem('shopeasy_cart', JSON.stringify(cart)); }

function toggleCart() {
  document.getElementById('cart-drawer').classList.toggle('open');
  document.getElementById('drawer-backdrop').classList.toggle('open');
}

// ─────────────────────────────────────────────────────────────────────────
// ORDERS
// ─────────────────────────────────────────────────────────────────────────
async function placeOrder() {
  if (!user) {
    toggleCart();
    openAuth('login');
    showToast('Please sign in to place an order', 'info');
    return;
  }
  if (!cart.length) { showToast('Your cart is empty', 'error'); return; }

  const btn = document.getElementById('checkout-btn');
  setLoading(btn, true, 'Placing Order...');

  try {
    const res = await fetch(`${API}/orders`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId:   user.userId,
        userName: user.name,
        items: cart.map(i => ({ productId: i.productId, quantity: i.quantity }))
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.message || data.error || 'Order failed');

    // Clear cart, close drawer
    cart = []; saveCart(); syncCartUI();
    toggleCart();
    showToast('🎉 Order placed successfully! Check your notifications.', 'success');

    // Refresh notification badge
    fetchNotifCount();

    // If user is on orders page, reload
    if (document.getElementById('page-orders').classList.contains('active')) loadOrders();
  } catch (e) {
    showToast(e.message, 'error');
  } finally {
    setLoading(btn, false, 'Place Order');
  }
}

async function loadOrders() {
  const container = document.getElementById('orders-container');
  if (!user) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">📦</div>
        <h3>Sign in to see your orders</h3>
        <p>Your order history will appear here</p>
        <button class="btn-primary" onclick="openAuth('login')">Sign In</button>
      </div>`;
    return;
  }

  container.innerHTML = '<div class="empty-state"><div class="skeleton-card" style="height:120px;border-radius:12px;width:100%;"></div></div>';

  try {
    const res    = await fetch(`${API}/orders/user/${user.userId}`);
    const orders = await res.json();

    if (!orders.length) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">🛍️</div>
          <h3>No orders yet</h3>
          <p>When you place an order it will show up here</p>
          <button class="btn-primary" onclick="showPage('products', document.querySelector('[data-page=products]'))">Start Shopping</button>
        </div>`;
      return;
    }

    container.innerHTML = orders.map(o => `
      <div class="order-card">
        <div class="order-top">
          <div>
            <div class="order-id">Order ID</div>
            <div class="order-num">#${o.id.substring(0,12).toUpperCase()}</div>
            <div class="order-date">${formatDate(o.createdAt)}</div>
          </div>
          <span class="status-badge status-${o.status}">${o.status}</span>
        </div>
        <div class="order-items">
          ${o.items.map(i => `
            <div class="order-item-row">
              <span class="order-item-name">${esc(i.productName)}</span>
              <span>×${i.quantity} &nbsp; $${(i.price * i.quantity).toFixed(2)}</span>
            </div>`).join('')}
        </div>
        <div class="order-total-row">
          <span class="order-total-label">Total</span>
          <span class="order-total-val">$${o.total.toFixed(2)}</span>
        </div>
      </div>`).join('');
  } catch (e) {
    container.innerHTML = `<div class="empty-state"><h3>Could not load orders</h3><p>${e.message}</p></div>`;
  }
}

// ─────────────────────────────────────────────────────────────────────────
// NOTIFICATIONS
// ─────────────────────────────────────────────────────────────────────────
async function loadNotifications() {
  const container = document.getElementById('notifications-container');
  if (!user) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🔔</div>
        <h3>Sign in to see notifications</h3>
        <button class="btn-primary" onclick="openAuth('login')">Sign In</button>
      </div>`;
    return;
  }

  try {
    const res   = await fetch(`${API}/notifications/${user.userId}`);
    const items = await res.json();

    if (!items.length) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">🔕</div>
          <h3>No notifications yet</h3>
          <p>Notifications from your orders will appear here</p>
        </div>`;
      return;
    }

    container.innerHTML = items.map(n => `
      <div class="notif-card ${n.read ? 'read' : 'unread'}" onclick="markRead('${n.id}',this)">
        <div class="notif-icon-wrap">${n.type === 'ORDER' ? '📦' : '🔔'}</div>
        <div class="notif-content">
          <div class="notif-msg">${esc(n.message)}</div>
          <div class="notif-time">${formatDate(n.createdAt)}</div>
        </div>
        ${!n.read ? '<div class="unread-dot"></div>' : ''}
      </div>`).join('');

    fetchNotifCount();
  } catch (e) {
    container.innerHTML = `<div class="empty-state"><h3>Could not load notifications</h3></div>`;
  }
}

async function fetchNotifCount() {
  if (!user) return;
  try {
    const res  = await fetch(`${API}/notifications/${user.userId}/unread-count`);
    const data = await res.json();
    const badge = document.getElementById('notif-badge');
    if (data.count > 0) { badge.textContent = data.count; badge.style.display = 'inline-flex'; }
    else badge.style.display = 'none';
  } catch {}
}

async function markRead(id, el) {
  try {
    await fetch(`${API}/notifications/${id}/read`, { method: 'PUT' });
    el.classList.remove('unread');
    el.classList.add('read');
    el.querySelector('.unread-dot')?.remove();
    fetchNotifCount();
  } catch {}
}

function startNotifPolling() {
  clearInterval(notifPollTimer);
  fetchNotifCount();
  notifPollTimer = setInterval(fetchNotifCount, 30000); // poll every 30s
}

// ─────────────────────────────────────────────────────────────────────────
// AUTH
// ─────────────────────────────────────────────────────────────────────────
async function login() {
  const email    = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  const btn      = document.getElementById('login-btn');

  if (!email || !password) { showErr('login-err', 'Please fill in all fields'); return; }

  setLoading(btn, true, 'Signing in...');
  clearErr('login-err');

  try {
    const res  = await fetch(`${API}/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || data.error || 'Invalid credentials');

    user = data;
    localStorage.setItem('shopeasy_user', JSON.stringify(user));
    syncAuthUI();
    closeAuth();
    showToast(`Welcome back, ${user.name}! 👋`, 'success');
    startNotifPolling();
    // Clear form
    document.getElementById('login-email').value = '';
    document.getElementById('login-password').value = '';
  } catch (e) {
    showErr('login-err', e.message);
  } finally {
    setLoading(btn, false, 'Sign In');
  }
}

async function register() {
  const name     = document.getElementById('reg-name').value.trim();
  const email    = document.getElementById('reg-email').value.trim();
  const password = document.getElementById('reg-password').value;
  const btn      = document.getElementById('register-btn');

  if (!name || !email || !password) { showErr('reg-err', 'Please fill in all fields'); return; }
  if (password.length < 6) { showErr('reg-err', 'Password must be at least 6 characters'); return; }

  setLoading(btn, true, 'Creating account...');
  clearErr('reg-err');

  try {
    const res  = await fetch(`${API}/users/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || data.error || 'Registration failed');

    user = data;
    localStorage.setItem('shopeasy_user', JSON.stringify(user));
    syncAuthUI();
    closeAuth();
    showToast(`Welcome to ShopEasy, ${user.name}! 🎉`, 'success');
    startNotifPolling();
    // Clear form
    ['reg-name','reg-email','reg-password'].forEach(id => document.getElementById(id).value = '');
  } catch (e) {
    showErr('reg-err', e.message);
  } finally {
    setLoading(btn, false, 'Create Account');
  }
}

function logout() {
  user = null;
  localStorage.removeItem('shopeasy_user');
  clearInterval(notifPollTimer);
  syncAuthUI();
  document.getElementById('notif-badge').style.display = 'none';
  showToast('You have been signed out', 'info');
}

function syncAuthUI() {
  if (user) {
    document.getElementById('auth-btns').style.display = 'none';
    document.getElementById('user-pill').style.display = 'flex';
    document.getElementById('user-display-name').textContent = user.name;
    document.getElementById('avatar-initials').textContent = user.name.charAt(0).toUpperCase();
  } else {
    document.getElementById('auth-btns').style.display = 'flex';
    document.getElementById('user-pill').style.display = 'none';
  }
}

// ─────────────────────────────────────────────────────────────────────────
// AUTH MODAL
// ─────────────────────────────────────────────────────────────────────────
function openAuth(tab = 'login') {
  document.getElementById('modal-backdrop').classList.add('open');
  document.getElementById('auth-modal').classList.add('open');
  switchTab(tab);
}
function closeAuth() {
  document.getElementById('modal-backdrop').classList.remove('open');
  document.getElementById('auth-modal').classList.remove('open');
}
function switchTab(tab) {
  document.getElementById('form-login').style.display    = tab === 'login'    ? 'block' : 'none';
  document.getElementById('form-register').style.display = tab === 'register' ? 'block' : 'none';
  document.getElementById('tab-login').classList.toggle('active',    tab === 'login');
  document.getElementById('tab-register').classList.toggle('active', tab === 'register');
}

// ─────────────────────────────────────────────────────────────────────────
// UTILS
// ─────────────────────────────────────────────────────────────────────────
function showToast(msg, type = 'info') {
  const container = document.getElementById('toast-container');
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `<span class="toast-icon">${icons[type]}</span><span>${msg}</span>`;
  container.appendChild(el);
  setTimeout(() => {
    el.style.animation = 'toastOut 0.3s ease forwards';
    setTimeout(() => el.remove(), 300);
  }, 3500);
}

function setLoading(btn, loading, text) {
  if (loading) {
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> ${text}`;
  } else {
    btn.disabled = false;
    btn.textContent = text;
  }
}

function showErr(id, msg) { document.getElementById(id).textContent = msg; }
function clearErr(id)     { document.getElementById(id).textContent = ''; }

function esc(str) {
  return String(str)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('en-US', {
    year:'numeric', month:'short', day:'numeric',
    hour:'2-digit', minute:'2-digit'
  });
}

/* ── AI Chat ─────────────────────────────────────────────────── */
let chatOpen = false;

function toggleChat() {
  chatOpen = !chatOpen;
  document.getElementById('chat-window').style.display = chatOpen ? 'flex' : 'none';
  document.getElementById('chat-badge').style.display  = 'none';
  if (chatOpen) document.getElementById('chat-input').focus();
}

function appendMsg(text, role) {
  const box = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = `chat-msg ${role}`;
  div.innerHTML = `<div class="msg-bubble">${escHtml(text)}</div>`;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
  return div;
}

function appendTyping() {
  const box = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'chat-msg bot';
  div.id = 'typing-indicator';
  div.innerHTML = '<div class="msg-bubble typing">ShopBot is thinking...</div>';
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

function removeTyping() {
  const el = document.getElementById('typing-indicator');
  if (el) el.remove();
}

async function sendChat() {
  const input = document.getElementById('chat-input');
  const msg   = input.value.trim();
  if (!msg) return;

  input.value = '';
  document.getElementById('chat-send-btn').disabled = true;
  document.getElementById('chat-suggestions').style.display = 'none';
  appendMsg(msg, 'user');
  appendTyping();

  try {
    const res = await fetch('/api/ai/chat', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ message: msg, userId: state.user?.id || null }),
    });
    const data = await res.json();
    removeTyping();
    appendMsg(data.reply || 'Sorry, I could not process that.', 'bot');
  } catch (e) {
    removeTyping();
    appendMsg('Connection error. Please try again.', 'bot');
  } finally {
    document.getElementById('chat-send-btn').disabled = false;
    input.focus();
  }
}

function sendSuggestion(text) {
  document.getElementById('chat-input').value = text;
  sendChat();
}
