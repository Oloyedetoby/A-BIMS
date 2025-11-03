<template>
  <div class="management-list">
    <div class="header-actions">
      <h2>Manage Authors</h2>
      <button class="btn-primary" @click="openCreateModal">+ Add New Author</button>
    </div>

    <div v-if="loading">Loading authors...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <table v-if="authors.length > 0">
      <thead>
        <tr>
          <th>Author Name</th>
          <th class="actions-cell">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="author in authors" :key="author.id">
          <td>{{ author.name }}</td>
          <td class="actions-cell">
            <button class="btn-edit" @click="openEditModal(author)">Edit</button>
            <button class="btn-danger" @click="openDeleteModal(author)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else-if="!loading" class="no-data">No authors found. Please add one.</p>

    <!-- The Modal for Creating and Editing Authors -->
    <AuthorFormModal 
      :show="showEditModal"
      :author="selectedAuthor"
      @close="closeModals"
      @author-saved="handleSave"
    />

    <!-- The Delete Confirmation Dialog -->
    <ConfirmDialog
      :show="showDeleteModal"
      title="Delete Author"
      :message="`Are you sure you want to delete '${selectedAuthor?.name}'? This may affect existing books.`"
      @cancel="closeModals"
      @confirm="deleteAuthor"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useToast } from 'vue-toastification';
import apiClient from '../api';
import AuthorFormModal from '../components/AuthorFormModal.vue';
import ConfirmDialog from '../components/ConfirmDialog.vue';

const toast = useToast();
const authors = ref([]);
const loading = ref(true);
const error = ref(null);

const showEditModal = ref(false);
const showDeleteModal = ref(false);
const selectedAuthor = ref(null);

const fetchAuthors = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/authors/');
    authors.value = response.data;
  } catch (err) {
    error.value = "Failed to fetch authors.";
  } finally {
    loading.value = false;
  }
};

onMounted(fetchAuthors);

const closeModals = () => {
  showEditModal.value = false;
  showDeleteModal.value = false;
  selectedAuthor.value = null;
};

const handleSave = () => {
  closeModals();
  fetchAuthors(); // Refresh the list
};

const openCreateModal = () => {
  selectedAuthor.value = null; // Ensure we're in "create" mode
  showEditModal.value = true;
};

const openEditModal = (author) => {
  selectedAuthor.value = author;
  showEditModal.value = true;
};

const openDeleteModal = (author) => {
  selectedAuthor.value = author;
  showDeleteModal.value = true;
};

const deleteAuthor = async () => {
  if (!selectedAuthor.value) return;
  try {
    await apiClient.delete(`/authors/${selectedAuthor.value.id}/`);
    toast.success("Author deleted successfully.");
    handleSave(); // Close modal and refresh
  } catch (err) {
    toast.error("Failed to delete author. It might be in use by a book.");
    console.error(err);
  }
};
</script>

<style scoped>
.management-list { max-width: 800px; margin: auto; }
.header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.btn-primary { background-color: #42b983; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
table { width: 100%; border-collapse: collapse; }
th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
th { background-color: #f2f2f2; }
.actions-cell { width: 180px; text-align: center; }
.actions-cell button { margin: 0 5px; padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
.btn-edit { background-color: #007bff; color: white; }
.btn-danger { background-color: #d0021b; color: white; }
.no-data { text-align: center; color: #666; padding: 20px; }
.error { color: red; font-weight: bold; }
</style>