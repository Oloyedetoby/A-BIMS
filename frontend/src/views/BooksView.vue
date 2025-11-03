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

    <div v-if="loading">Loading books...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <table v-if="books.length > 0">
      <thead>
        <tr>
          <th>Title</th>
          <th>Author</th>
          <th>Publisher</th>
          <th class="text-right">Price</th>
          <th class="text-right">In Stock</th>
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
    <div v-else-if="!loading">
      <p>No books found matching your criteria.</p>
    </div>

    <!-- The Modal for Creating and Editing Books -->
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
import apiClient from '../api';
import BookFormModal from '../components/BookFormModal.vue';

const router = useRouter();
const books = ref([]);
const loading = ref(true);
const error = ref(null);
let debounceTimer = null;

// State for filters and search
const searchTerm = ref('');
const authors = ref([]);
const publishers = ref([]);
const selectedAuthor = ref('');
const selectedPublisher = ref('');

// State for the modal
const showModal = ref(false);

const viewBook = (bookId) => {
  router.push(`/books/${bookId}`);
};

// Modal controls
const openCreateModal = () => {
  showModal.value = true;
};
const handleBookSaved = () => {
  showModal.value = false;
  fetchBooks(); // Refresh the list
};

const fetchBooks = async () => {
  loading.value = true;
  error.value = null;
  try {
    const params = {};
    if (searchTerm.value) params.search = searchTerm.value;
    if (selectedAuthor.value) params.author = selectedAuthor.value;
    if (selectedPublisher.value) params.publisher = selectedPublisher.value;
    
    const response = await apiClient.get('/books/', { params });
    books.value = response.data;
  } catch (err) {
    error.value = 'Failed to fetch books.';
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
        console.error("Failed to fetch filter data:", err);
    }
};

const debouncedFetchBooks = () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(fetchBooks, 300);
};

onMounted(() => {
  fetchBooks();
  fetchFilterData();
});

const formatPrice = (value) => {
  const num = parseFloat(value);
  return isNaN(num) ? '0.00' : num.toFixed(2);
};
</script>

<style scoped>
/* Using the same robust styling from the Customers page */
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
.error { color: red; font-weight: bold; }
</style>