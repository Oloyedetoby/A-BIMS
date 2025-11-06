<template>
  <div>
    <div v-if="loading">Loading publisher details...</div>
    <div v-if="error" class="error">{{ error }}</div>
    
    <div v-if="publisher">
      <h1>{{ publisher.name }}</h1>
      <div class="contact-details">
        <p v-if="publisher.contact_person"><strong>Contact:</strong> {{ publisher.contact_person }}</p>
        <p v-if="publisher.phone_number"><strong>Phone:</strong> {{ publisher.phone_number }}</p>
      </div>
      
      <div class="books-section">
        <h3>Books from this Publisher</h3>
        <div v-if="publisher.books && publisher.books.length > 0">
          <table>
            <thead>
              <tr>
                <th>Title</th>
                <th>Author</th>
                <th class="text-right">Price</th>
                <th class="text-right">In Stock</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="book in publisher.books" :key="book.id" @click="viewBook(book.id)" class="clickable-row">
                <td>{{ book.title }}</td>
                <td>{{ book.author }}</td>
                <td class="text-right">₦{{ formatPrice(book.price) }}</td>
                <td class="text-right">{{ book.quantity_in_stock }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else>There are currently no books from this publisher in the system.</p>
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
const publisher = ref(null);
const loading = ref(true);
const error = ref(null);

onMounted(async () => {
  const publisherId = route.params.id;
  try {
    const response = await apiClient.get(`/publishers/${publisherId}/`);
    publisher.value = response.data;
  } catch (err) {
    error.value = 'Failed to fetch publisher details.';
    console.error(err);
  } finally {
    loading.value = false;
  }
});

const viewBook = (bookId) => {
  router.push({ name: 'BookDetail', params: { id: bookId } });
};

const formatPrice = (value) => {
  const num = parseFloat(value);
  return isNaN(num) ? '0.00' : num.toFixed(2);
};
</script>

<style scoped>
h1 { border-bottom: 1px solid #eee; padding-bottom: 15px; }
.contact-details { margin: 20px 0; color: #555; }
.books-section { margin-top: 30px; }
table { width: 100%; border-collapse: collapse; margin-top: 15px; }
th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
th { background-color: #f2f2f2; }
.text-right { text-align: right; }
.clickable-row { cursor: pointer; }
.clickable-row:hover { background-color: #f5f5f5; }
</style>