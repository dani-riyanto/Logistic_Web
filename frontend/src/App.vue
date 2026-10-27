<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import HeaderNav from './components/HeaderNav.vue'
import DashboardBanner from './components/DashboardBanner.vue'
import DashboardStats from './components/DashboardStats.vue'
import OrderForm from './components/OrderForm.vue'
import OrderList from './components/OrderList.vue'
import SiteFooter from './components/SiteFooter.vue'
import { fetchOrders, createOrder, deleteOrder, updateOrder } from './services/api.js'
import MenuForm from './components/MenuForm.vue'

const orders = ref([])
const loading = ref(false)
const error = ref(null)
const serverError = ref('')
const isSubmitting = ref(false)
const searchQuery = ref('')
const activeTab = ref('Semua')

let abortController = null

const loadOrders = async () => {
  if (abortController) abortController.abort()
  abortController = new AbortController()
  loading.value = true
  error.value = null

  try {
    const data = await fetchOrders(searchQuery.value, abortController.signal)
    orders.value = Array.isArray(data) ? data : (data.data || [])
  } catch (err) {
    if (err.name !== 'AbortError') {
      error.value = err.message || 'Gagal terhubung ke server FastAPI (http://localhost:8000).'
    }
  } finally {
    loading.value = false
  }
}

let searchDebounce = null
watch(searchQuery, () => {
  clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => { loadOrders() }, 300)
})

onMounted(() => { loadOrders() })

onUnmounted(() => {
  if (abortController) abortController.abort()
  if (searchDebounce) clearTimeout(searchDebounce)
})

const filteredOrders = computed(() => {
  if (activeTab.value === 'Semua') return orders.value
  return orders.value.filter(o => o.status === activeTab.value)
})

const handleCreateOrder = async (orderData, resetFn) => {
  isSubmitting.value = true
  serverError.value = ''
  try {
    await createOrder(orderData)
    resetFn()
    await loadOrders()
  } catch (err) {
    serverError.value = err.message
  } finally {
    isSubmitting.value = false
  }
}

const handleDeleteOrder = async (id) => {
  try {
    await deleteOrder(id)
    await loadOrders()
  } catch (err) {
    alert(`Gagal menghapus: ${err.message}`)
  }
}
const props = defineProps({
  isSubmitting: Boolean,
  serverError: String
})

const handleMenuAdded = () => {
  // Karena order form mengambil data menu dari database,
  // kita bisa memaksa reload halaman agar form pesanan mengambil menu terbaru
  window.location.reload() 
}

const emit = defineEmits(['create-order'])

// State untuk menyimpan daftar menu dari database
const daftarMenu = ref([])
const form = ref({
  nama_pelanggan: '',
  menu_id: '',
  catatan: ''
})

// Ambil data dari API backend saat komponen ini dirender
onMounted(async () => {
  try {
    const data = await fetchMenus()
    daftarMenu.value = data
  } catch (error) {
    console.error("Gagal load menu:", error)
  }
})

const handleUpdateOrder = async (order) => {
  // Memunculkan prompt untuk mengubah status (Baru, Diproses, Selesai)
  const newStatus = prompt(`Ubah status untuk ${order.customer_name}:`, order.status)
  
  if (newStatus && newStatus !== order.status) {
    try {
      // Panggil fungsi API updateOrder (pastikan sudah ada di api.js)
      await updateOrder(order.id, { status: newStatus })
      await loadOrders() // Refresh data
    } catch (err) {
      alert(`Gagal update: ${err.message}`)
    }
  }
}

// ... (biarkan fungsi submit Anda yang sudah ada) ...
</script>

<template>
  <div class="min-h-screen bg-white font-sans text-body">
    <HeaderNav />
    <DashboardBanner />
    <DashboardStats :orders="orders" />
    <main class="bg-white">
      <div class="container grid grid-cols-1 gap-8 py-8 sm:py-10 lg:grid-cols-12">
        
        
        <div class="lg:col-span-5 lg:sticky lg:top-6 lg:self-start">
          <OrderForm :is-submitting="isSubmitting" :server-error="serverError" @create-order="handleCreateOrder" />
          
       >
          <MenuForm @menu-added="handleMenuAdded" />
        </div>

    
        <div class="lg:col-span-7">
         <OrderList 
            :orders="filteredOrders" 
            :loading="loading" 
            :error="error" 
            v-model:searchQuery="searchQuery"
            v-model:activeTab="activeTab" 
            @retry-fetch="loadOrders" 
            @delete-order="handleDeleteOrder" 
            @update-order="handleUpdateOrder" 
          />
        </div>

      </div>
    </main>

    <SiteFooter />
  </div>
</template>
