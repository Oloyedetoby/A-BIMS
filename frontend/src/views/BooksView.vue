<template>
  <div class="book-list">
    <div class="header-actions">
      <h2>Book List</h2>
      <div class="controls">
        <button class="btn-primary" @click="openCreateModal">+ Add New Book</button>
        <div class="filters">
          <select v-model="selectedPublisher" @change="fetchBooks">
            <option value="">All Publishers</option>
            <option v-for="pub in publishers" :key="pub.id" :value="pub.id">{{ pub.name }}</option>
          </select>
          <select v-model="selectedAuthor" @change="fetchBooks">
            <option value="">All Authors</option>
            <option v-for="author in authors" :key="author.id" :value="author.id">{{ author.name }}</option>
          </select>
          <input 
            type="text" 
            v-model="searchTerm" 
            placeholder="Search by title..."
            @input="debouncedFetchBooks"
          >
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">Loading books...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <table v-if="books.length > 0">
      <thead>
        <tr>
          <th @click="sortBy('title')" class="sortable">
            Title <span v-if="sortField === 'title'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span>
          </th>
          <th>Author</th>
          <th>Publisher</th>
          <th @click="sortBy('price')" class="sortable text-right">
            Price <span v-if="sortField === 'price'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span>
          </th>
          <th @click="sortBy('quantity_in_stock')" class="sortable text-right">
            In Stock <span v-if="sortField === 'quantity_in_stock'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="book in books" :key="book.id" @click="viewBook(book.id)" class="clickable-row">
          <td>{{ book.title }}</td>
          <td>{{ book.author }}</td>
          <td>{{ book.publisher }}</td>
          <td class="text-right">₦{{ formatPrice(book.price) }}</td>
          <td class="text-right">{{ book.quantity_in_stock }}</td>
        </tr>
      </tbody>
    </table>
    <div v-else-if="!loading" class="no-data">
      <p>No books found matching your criteria.</p>
    </div>

    <BookFormModal 
      :show="showModal"
      :book="null" 
      @close="showModal = false"
      @book-saved="handleBookSaved"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import apiClient from '../api';
import BookFormModal from '../components/BookFormModal.vue';

const router = useRouter();
const toast = useToast();
const books = ref([]);
const loading = ref(true);
const error = ref(null);
let debounceTimer = null;

const searchTerm = ref('');
const authors = ref([]);
const publishers = ref([]);
const selectedAuthor = ref('');
const selectedPublisher = ref('');
const sortField = ref('title');
const sortDir = ref('asc');
const showModal = ref(false);

const viewBook = (bookId) => {
  router.push(`/books/${bookId}`);
};

const openCreateModal = () => {
  showModal.value = true;
};
const handleBookSaved = () => {
  showModal.value = false;
  fetchBooks();
};

const fetchBooks = async () => {
  loading.value = true;
  error.value = null;
  try {
    const params = {};
    if (searchTerm.value) params.search = searchTerm.value;
    if (selectedAuthor.value) params.author = selectedAuthor.value;
    if (selectedPublisher.value) params.publisher = selectedPublisher.value;
    params.ordering = `${sortDir.value === 'desc' ? '-' : ''}${sortField.value}`;
    
    const response = await apiClient.get('/books/', { params });
    books.value = response.data;
  } catch (err) {
    error.value = 'Failed to fetch books.';
    toast.error(error.value);
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const fetchFilterData = async () => {
    try {
        const [authorRes, pubRes] = await Promise.all([
            apiClient.get('/authors/'),
            apiClient.get('/publishers/'),
        ]);
        authors.value = authorRes.data;
        publishers.value = pubRes.data;
    } catch (err) {
        toast.error("Failed to load filter options.");
        console.error("Failed to fetch filter data:", err);
    }
};

const debouncedFetchBooks = () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(fetchBooks, 300);
};

const sortBy = (field) => {
  if (sortField.value === field) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortField.value = field;
    sortDir.value = (field === 'price' || field === 'quantity_in_stock') ? 'desc' : 'asc';
  }
  fetchBooks();
};

onMounted(() => {
  fetchBooks();
  fetchFilterData();
});

const formatPrice = (value) => {
  const num = parseFloat(value);
  return isNaN(num) ? '0.00' : num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
};
</script>

<style scoped>
.header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.controls { display: flex; gap: 15px; align-items: center; }
.btn-primary { background-color: #42b983; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; font-weight: bold; border: none; cursor: pointer; }
.clickable-row { cursor: pointer; transition: background-color 0.2s ease; }
.clickable-row:hover { background-color: #f5f5f5; }
.filters { display: flex; gap: 15px; }
.filters input, .filters select { padding: 8px 12px; font-size: 1rem; border: 1px solid #ccc; border-radius: 4px; }
.filters input { width: 250px; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; }
th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
th { background-color: #f2f2f2; }
.text-right { text-align: right; }
.sortable { cursor: pointer; user-select: none; }
.sortable:hover { background-color: #e9ecef; }
.sortable span { font-size: 0.8em; padding-left: 5px; }
.no-data, .loading-state { text-align: center; color: #666; padding: 20px; font-style: italic; }
.error { color: red; font-weight: bold; }
</style>