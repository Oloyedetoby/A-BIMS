<template>
  <div>
    <div v-if="loading">Loading book details...</div>
    <div v-if="error" class="error">{{ error }}</div>
    
    <div v-if="book" class="book-dashboard">
      <!-- Header -->
      <div class="header">
        <h1>{{ book.title }}</h1>
        <div class="header-actions">
          <button class="btn-primary" @click="showEditModal = true">Edit Book</button>
          <button class="btn-danger" @click="showDeleteModal = true">Delete Book</button>
        </div>
      </div>
      <p class="author-publisher">by {{ book.author?.name }} | Published by {{ book.publisher?.name }}</p>

      <!-- Summary Cards -->
      <div class="stats-container">
        <div class="stat-card">
          <h3>List Price</h3>
          <p>₦{{ formatPrice(book.price) }}</p>
        </div>
        <div class="stat-card stock" :class="{ 'low-stock': book.quantity_in_stock < 10 }">
          <h3>In Stock</h3>
          <p>{{ book.quantity_in_stock }}</p>
        </div>
        <div class="stat-card">
          <h3>Units Sold</h3>
          <p>{{ bookStats.unitsSold }}</p>
        </div>
        <div class="stat-card">
          <h3>Total Revenue</h3>
          <p>₦{{ formatPrice(bookStats.totalRevenue) }}</p>
        </div>
      </div>

      <!-- Sales History -->
      <div class="sales-history">
        <h3>Sales History</h3>
        <div v-if="book.sale_history && book.sale_history.length > 0">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Customer</th>
                <th>Invoice #</th>
                <th>Quantity Sold</th>
                <th>Unit Price</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="sale in book.sale_history" :key="`${sale.invoice_id}-${book.id}`">
                <td>{{ sale.date }}</td>
                <td>{{ sale.customer_name }}</td>
                <td>
                  <router-link :to="{ name: 'Invoices' }">#{{ sale.invoice_id }}</router-link>
                </td>
                <td>{{ sale.quantity }}</td>
                <td>₦{{ formatPrice(sale.unit_price) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else>This book has not been sold yet.</p>
      </div>
    </div>

    <!-- The Edit Book Modal -->
    <BookFormModal 
      v-if="book"
      :show="showEditModal"
      :book="book"
      @close="showEditModal = false"
      @book-saved="handleBookSaved"
    />

    <!-- The Delete Confirmation Dialog -->
    <ConfirmDialog 
      :show="showDeleteModal"
      title="Delete Book"
      :message="`Are you sure you want to delete '${book?.title}'? This action cannot be undone.`"
      @cancel="showDeleteModal = false"
      @confirm="deleteBook"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import apiClient from '../api';
import BookFormModal from '../components/BookFormModal.vue';
import ConfirmDialog from '../components/ConfirmDialog.vue';

const route = useRoute();
const router = useRouter();
const toast = useToast();
const book = ref(null);
const loading = ref(true);
const error = ref(null);
const showEditModal = ref(false);
const showDeleteModal = ref(false);

const fetchBookData = async () => {
  loading.value = true;
  const bookId = route.params.id;
  try {
    const response = await apiClient.get(`/books/${bookId}/`);
    book.value = response.data;
  } catch (err) {
    error.value = 'Failed to fetch book details.';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const deleteBook = async () => {
  if (!book.value) return;
  try {
    await apiClient.delete(`/books/${book.value.id}/`);
    toast.success(`Book "${book.value.title}" deleted successfully.`);
    showDeleteModal.value = false;
    router.push('/books');
  } catch (err) {
    toast.error("Failed to delete book.");
    console.error(err);
  }
};

onMounted(fetchBookData);

const handleBookSaved = () => {
  showEditModal.value = false;
  fetchBookData();
};

const bookStats = computed(() => {
  if (!book.value || !book.value.sale_history) {
    return { unitsSold: 0, totalRevenue: 0 };
  }
  const unitsSold = book.value.sale_history.reduce((sum, sale) => sum + sale.quantity, 0);
  const totalRevenue = book.value.sale_history.reduce((sum, sale) => {
    return sum + (sale.quantity * parseFloat(sale.unit_price || 0));
  }, 0);
  return { unitsSold, totalRevenue };
});

const formatPrice = (value) => {
  const num = parseFloat(value);
  if (isNaN(num)) return '0.00';
  return num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
};
</script>

<style scoped>
.header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
}
.header-actions {
  display: flex;
  gap: 10px;
}
h1 { margin-bottom: 0; }
.btn-primary {
  background-color: #007bff;
  color: white;
  padding: 8px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.btn-danger {
  background-color: #d0021b;
  color: white;
  padding: 8px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.author-publisher { 
  color: #555; 
  margin-top: 5px; 
  border-bottom: 1px solid #eee; 
  padding-bottom: 20px; 
}
.stats-container { 
  display: flex; 
  gap: 20px; 
  margin: 20px 0; 
}
.stat-card { 
  background-color: #f9f9f9; 
  border: 1px solid #ddd; 
  border-radius: 8px; 
  padding: 20px; 
  flex-grow: 1; 
  text-align: center; 
}
.stat-card h3 { 
  margin: 0 0 10px 0; 
  font-size: 1rem; 
  color: #555; 
}
.stat-card p { 
  margin: 0; 
  font-size: 2rem; 
  font-weight: bold; 
}
.stat-card.stock p { 
  color: #28a745; 
}
.stat-card.low-stock p { 
  color: #d0021b; 
}
.sales-history {
  margin-top: 30px;
}
.sales-history table { 
  width: 100%; 
  border-collapse: collapse; 
  margin-top: 15px; 
}
.sales-history th, .sales-history td { 
  border: 1px solid #ddd; 
  padding: 12px; 
  text-align: left; 
}
.sales-history th { 
  background-color: #f2f2f2; 
}
.error {
  color: red;
  font-weight: bold;
}
</style>