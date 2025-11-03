<template>
  <PaymentModal :show="show" @close="$emit('close')">
    <form @submit.prevent="submitForm">
      <h3>{{ editableAuthor && editableAuthor.id ? 'Edit Author' : 'Add New Author' }}</h3>
      <div class="form-group">
        <label for="author-name">Author Name:</label>
        <input type="text" id="author-name" v-model="editableAuthor.name" required>
      </div>
      <div class="form-actions">
        <button type="button" @click="$emit('close')" class="btn-secondary">Cancel</button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Saving...' : 'Save Author' }}
        </button>
      </div>
       <div v-if="error" class="error">{{ error }}</div>
    </form>
  </PaymentModal>
</template>

<script setup>
import { ref, watchEffect } from 'vue';
import { useToast } from 'vue-toastification';
import apiClient from '../api';
import PaymentModal from './PaymentModal.vue';

const props = defineProps({ show: Boolean, author: Object });
const emit = defineEmits(['close', 'author-saved']);
const toast = useToast();

const editableAuthor = ref({ name: '' });
const isSubmitting = ref(false);
const error = ref(null);

watchEffect(() => {
  if (props.author) {
    editableAuthor.value = { ...props.author }; // For editing
  } else {
    editableAuthor.value = { name: '' }; // For creating
  }
});

const submitForm = async () => {
  isSubmitting.value = true;
  error.value = null;
  try {
    if (editableAuthor.value.id) {
      await apiClient.put(`/authors/${editableAuthor.value.id}/`, editableAuthor.value);
      toast.success("Author updated successfully!");
    } else {
      await apiClient.post('/authors/', editableAuthor.value);
      toast.success("Author added successfully!");
    }
    emit('author-saved');
  } catch (err) {
    error.value = "Failed to save author. Name might already exist.";
    toast.error(error.value);
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
h3 { margin-top: 0; }
.form-group { margin-bottom: 20px; }
.form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
.form-group input { width: 100%; padding: 10px; font-size: 1rem; border-radius: 4px; border: 1px solid #ccc; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.btn-primary, .btn-secondary { padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
.btn-primary { background-color: #42b983; color: white; }
.btn-secondary { background-color: #6c757d; color: white; }
.error { color: red; margin-top: 10px; text-align: right; }
</style>