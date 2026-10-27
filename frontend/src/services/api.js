const BASE_URL = 'http://localhost:8000';

export async function fetchOrders(search = '', signal = null) {
  const params = new URLSearchParams({ skip: 0, limit: 10 });
  if (search) params.append('search', search);

  const res = await fetch(`${BASE_URL}/sessions?${params.toString()}`, { signal });
  if (!res.ok) throw new Error(`Gagal mengambil data (${res.status})`);
  return await res.json();
}

export async function createOrder(orderData) {
  const res = await fetch(`${BASE_URL}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(orderData)
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    
    // --- TAMBAHAN BARU UNTUK MENCEGAH [object Object] ---
    if (Array.isArray(errorData.detail)) {
      throw new Error(errorData.detail[0].msg); // Mengambil pesan spesifik dari FastAPI
    }
    // ----------------------------------------------------
    
    throw new Error(errorData.detail || errorData.message || `Gagal menambah pesanan (${res.status})`);
  }
  return await res.json();
}

// Update delete order function
export async function deleteOrder(id) {
  const res = await fetch(`${BASE_URL}/sessions/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`Gagal menghapus pesanan (${res.status})`);
  return true;
}

// Fetch menus function
export async function fetchMenus() {
  const res = await fetch(`${BASE_URL}/menus`);
  if (!res.ok) throw new Error(`Gagal mengambil data menu (${res.status})`);
  return await res.json();
}

// Update order function
export async function updateOrder(id, data) {
  const res = await fetch(`${BASE_URL}/sessions/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error(`Gagal update (${res.status})`);
  return await res.json();
}

// Create Menu function
export async function createMenu(menuData) {
  const res = await fetch(`${BASE_URL}/menus`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(menuData)
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Gagal menambah menu (${res.status})`);
  }
  return await res.json();
}