<template>
  <PaymentModal :show="show" @close="$emit('close')">
    <form @submit.prevent="submitForm">
      <h3>{{ isEditMode ? 'Edit Book' : 'Add New Book' }}</h3>
      
      <div class="form-group">
        <label for="book-title">Title:</label>
        <input type="text" id="book-title" v-model="editableBook.title" required>
      </div>
      <div class="form-group">
        <label for="book-price">Price:</label>
        <input type="number" id="book-price" step="0.01" v-model="editableBook.price" required>
      </div>
      <div class="form-group">
        <label for="book-stock">Quantity In Stock:</label>
        <input type="number" id="book-stock" v-model.number="editableBook.quantity_in_stock" required>
      </div>
      <div class="form-group">
        <label for="book-author">Author:</label>
        <select id="book-author" v-model="editableBook.author_id" required>
          <option disabled value="">Select an author</option>
          <option v-for="author in authors" :key="author.id" :value="author.id">{{ author.name }}</option>
        </select>
      </div>
      <div class="form-group">
        <label for="book-publisher">Publisher:</label>
        <select id="book-publisher" v-model="editableBook.publisher_id" required>
          <option disabled value="">Select a publisher</option>
          <option v-for="pub in publishers" :key="pub.id" :value="pub.id">{{ pub.name }}</option>
        </select>
      </div>

      <div class="form-actions">
        <button type="button" @click="$emit('close')" class="btn-secondary">Cancel</button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Saving...' : 'Save Book' }}
        </button>
      </div>
      <div v-if="error" class="error">{{ error }}</div>
    </form>
  </PaymentModal>
</template>

<script setup>
// CHANGE: We now import watchEffect instead of watch
import { ref, watchEffect, onMounted, computed } from 'vue';
import apiClient from '../api';
import PaymentModal from './PaymentModal.vue';
import { useToast } from 'vue-toastification';

const props = defineProps({ show: Boolean, book: Object });
const emit = defineEmits(['close', 'book-saved']);
const toast = useToast();

const editableBook = ref({});
const authors = ref([]);
const publishers = ref([]);
const isSubmitting = ref(false);
const error = ref(null);

const isEditMode = computed(() => !!props.book);

// THIS IS THE KEY FIX: We replace the 'watch' block with 'watchEffect'
watchEffect(() => {
  if (props.book) {
    // We are in 'Edit' mode. Copy the prop data to our local state.
    editableBook.value = { 
      ...props.book, 
      author_id: props.book.author?.id, 
      publisher_id: props.book.publisher?.id 
    };
  } else {
    // We are in 'Create' mode. Set default empty values.
    editableBook.value = { 
        title: '',
        price: 0.00,
        quantity_in_stock: 0,
        author_id: '',
        publisher_id: '',
    };
  }
});

onMounted(async () => {
  try {
    const [authorRes, pubRes] = await Promise.all([
      apiClient.get('/authors/'),
      apiClient.get('/publishers/')
    ]);
    authors.value = authorRes.data;
    publishers.value = pubRes.data;
  } catch (err) {
    toast.error("Failed to load author/publisher list.");
    console.error("Failed to load form data", err);
  }
});

const submitForm = async () => {
  isSubmitting.value = true;
  error.value = null;
  
  const payload = {
    title: editableBook.value.title,
    price: editableBook.value.price,
    quantity_in_stock: editableBook.value.quantity_in_stock,
    author_id: editableBook.value.author_id,
    publisher_id: editableBook.value.publisher_id,
  };

  try {
    if (isEditMode.value) {
      await apiClient.put(`/books/${props.book.id}/`, payload);
      toast.success("Book updated successfully!");
    } else {
      // Logic for creating a new book
      await apiClient.post('/books/', payload);
      toast.success("Book created successfully!");
    }
    emit('book-saved');
  } catch (err) {
    error.value = 'Failed to save book.';
    toast.error(error.value);
    console.error("API Error Response:", err.response?.data);
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.form-group { margin-bottom: 15px; }
.form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
.form-group input, .form-group select { width: 100%; padding: 10px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; }
.form-actions { margin-top: 20px; text-align: right; display: flex; gap: 10px; justify-content: flex-end; }
.btn-primary { background-color: #42b983; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; }
.btn-secondary { background-color: #6c757d; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; }
.error { color: red; margin-top: 10px; }
</style>