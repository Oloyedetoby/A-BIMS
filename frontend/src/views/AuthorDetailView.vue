<template>
  <div>
    <div v-if="loading">Loading author details...</div>
    <div v-if="error" class="error">{{ error }}</div>
    
    <div v-if="author">
      <h1>{{ author.name }}</h1>
      
      <div class="books-section">
        <h3>Books by this Author</h3>
        <div v-if="author.books && author.books.length > 0">
          <table>
            <thead>
              <tr>
                <th>Title</th>
                <th>Publisher</th>
                <th class="text-right">Price</th>
                <th class="text-right">In Stock</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="book in author.books" :key="book.id" @click="viewBook(book.id)" class="clickable-row">
                <td>{{ book.title }}</td>
                <td>{{ book.publisher }}</td>
                <td class="text-right">₦{{ book.price }}</td>
                <td class="text-right">{{ book.quantity_in_stock }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else>There are currently no books by this author in the system.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '../api';

const route = useRoute();
const router = useRouter();
const author = ref(null);
const loading = ref(true);
const error = ref(null);

onMounted(async () => {
  const authorId = route.params.id;
  try {
    const response = await apiClient.get(`/authors/${authorId}/`);
    author.value = response.data;
  } catch (err) {
    error.value = 'Failed to fetch author details.';
    console.error(err);
  } finally {
    loading.value = false;
  }
});

const viewBook = (bookId) => {
  router.push({ name: 'BookDetail', params: { id: bookId } });
};
</script>
<style scoped>
/* Add styling similar to our other pages */
h1 { border-bottom: 1px solid #eee; padding-bottom: 15px; }
.books-section { margin-top: 30px; }
table { width: 100%; border-collapse: collapse; margin-top: 15px; }
th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
th { background-color: #f2f2f2; }
.text-right { text-align: right; }
.clickable-row { cursor: pointer; }
.clickable-row:hover { background-color: #f5f5f5; }
</style>