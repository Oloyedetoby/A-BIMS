<template>
  <div class="book-list">
    <h2>Book List</h2>

    <div v-if="loading">Loading books...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <table v-if="books.length > 0">
      <thead>
        <tr>
          <th>Title</th>
          <th>Author</th>
          <th>Publisher</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="book in books" :key="book.id">
          <td>{{ book.title }}</td>
          <td>{{ book.author }}</td>
          <td>{{ book.publisher }}</td>
        </tr>
      </tbody>
    </table>
    <div v-else-if="!loading">
      No books found. Please add some in the admin panel.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api';

// Reactive variables
const books = ref([]);
const loading = ref(true);
const error = ref(null);

// Fetch data when the component is mounted
onMounted(async () => {
  try {
    // Make a GET request to our Django API books endpoint
    const response = await apiClient.get('/books/');
    books.value = response.data;
  } catch (err) {
    error.value = 'Failed to fetch books. Is the Django server running?';
    console.error(err);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
/* Styles are scoped to this component */
.book-list {
  width: 100%;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}
th, td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}
th {
  background-color: #f2f2f2;
}
.error {
  color: red;
  font-weight: bold;
}
</style>