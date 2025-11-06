<template>
  <div class="management-list">
    <div class="header-actions">
      <h2>{{ title }}</h2>
      <div class="controls">
        <input 
          type="text" 
          v-model="searchTerm" 
          :placeholder="`Search ${itemName.toLowerCase()}...`"
          @input="debouncedFetch"
        >
        <button class="btn-primary" @click="openCreateModal">+ Add New {{ singularItemName }}</button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">Loading...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <table v-if="items.length > 0">
      <thead>
        <tr>
          <th>Name</th>
          <th class="actions-cell">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" 
            :key="item.id" 
            @click="viewDetail(item.id)" 
            :class="{ 'clickable-row': detailRouteName }">
          <td>{{ item.name }}</td>
          <td class="actions-cell">
            <button class="btn-edit" @click.stop="openEditModal(item)">Edit</button>
            <button class="btn-danger" @click.stop="openDeleteModal(item)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else-if="!loading" class="no-data">No {{ itemName.toLowerCase() }} found.</p>
    
    <!-- Form Modal for Create/Edit -->
    <PaymentModal :show="showEditModal" @close="closeModals">
      <form @submit.prevent="submitForm">
        <h3>{{ editableItem && editableItem.id ? 'Edit' : 'Add New' }} {{ singularItemName }}</h3>
        <div class="form-group">
          <label for="item-name">Name:</label>
          <input type="text" id="item-name" v-model="editableItem.name" required>
        </div>
        <div class="form-actions">
          <button type="button" @click="closeModals" class="btn-secondary">Cancel</button>
          <button type="submit" class="btn-primary" :disabled="isSubmitting">
            {{ isSubmitting ? 'Saving...' : 'Save' }}
          </button>
        </div>
        <div v-if="formError" class="error">{{ formError }}</div>
      </form>
    </PaymentModal>

    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog
      :show="showDeleteModal"
      :title="`Delete ${singularItemName}`"
      :message="`Are you sure you want to delete '${selectedItem?.name}'? This could affect existing records.`"
      @cancel="closeModals"
      @confirm="deleteItem"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watchEffect, computed } from 'vue';
import { useToast } from 'vue-toastification';
import { useRouter } from 'vue-router';
import apiClient from '../api';
import PaymentModal from './PaymentModal.vue';
import ConfirmDialog from './ConfirmDialog.vue';

const props = defineProps({
  title: String,
  apiEndpoint: String,
  itemName: String,
  detailRouteName: String, // e.g., 'AuthorDetail'
});

const router = useRouter();
const toast = useToast();

const items = ref([]);
const loading = ref(true);
const error = ref(null);
const formError = ref(null);

const showEditModal = ref(false);
const showDeleteModal = ref(false);
const selectedItem = ref(null);
const editableItem = ref({ name: '' });
const isSubmitting = ref(false);

const searchTerm = ref('');
let debounceTimer = null;

const singularItemName = computed(() => {
    if (props.itemName.endsWith('es')) {
        return props.itemName.slice(0, -2);
    }
    return props.itemName.slice(0, -1);
});

const fetchData = async () => {
  loading.value = true;
  error.value = null;
  try {
    const params = {};
    if (searchTerm.value) {
      params.search = searchTerm.value;
    }
    const response = await apiClient.get(`/${props.apiEndpoint}/`, { params });
    items.value = response.data;
  } catch (err) {
    error.value = `Failed to fetch ${props.itemName.toLowerCase()}.`;
    toast.error(error.value);
  } finally {
    loading.value = false;
  }
};
onMounted(fetchData);

const debouncedFetch = () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(fetchData, 300);
};

// --- Navigation ---
const viewDetail = (itemId) => {
  if (props.detailRouteName) {
    router.push({ name: props.detailRouteName, params: { id: itemId } });
  }
};

watchEffect(() => {
  editableItem.value = selectedItem.value ? { ...selectedItem.value } : { name: '' };
});

const closeModals = () => {
  showEditModal.value = false;
  showDeleteModal.value = false;
  selectedItem.value = null;
  formError.value = null;
};

const handleSave = () => {
  closeModals();
  fetchData();
};

const openCreateModal = () => { selectedItem.value = null; showEditModal.value = true; };
const openEditModal = (item) => { selectedItem.value = item; showEditModal.value = true; };
const openDeleteModal = (item) => { selectedItem.value = item; showDeleteModal.value = true; };

const submitForm = async () => {
  isSubmitting.value = true;
  formError.value = null;
  try {
    if (editableItem.value.id) {
      await apiClient.put(`/${props.apiEndpoint}/${editableItem.value.id}/`, editableItem.value);
      toast.success(`${singularItemName.value} updated successfully!`);
    } else {
      await apiClient.post(`/${props.apiEndpoint}/`, editableItem.value);
      toast.success(`${singularItemName.value} added successfully!`);
    }
    handleSave();
  } catch (err) {
    formError.value = `Failed to save. The name may already exist.`;
    toast.error(`Failed to save ${singularItemName.value.toLowerCase()}.`);
  } finally {
    isSubmitting.value = false;
  }
};

const deleteItem = async () => {
  try {
    await apiClient.delete(`/${props.apiEndpoint}/${selectedItem.value.id}/`);
    toast.success(`${singularItemName.value} deleted successfully.`);
    handleSave();
  } catch (err) {
    toast.error(`Failed to delete ${singularItemName.value.toLowerCase()}. It may be in use by other records.`);
  }
};
</script>

<style scoped>
.management-list { max-width: 800px; margin: auto; }
.header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.controls { display: flex; gap: 15px; align-items: center; }
.controls input { padding: 8px 12px; font-size: 1rem; border: 1px solid #ccc; border-radius: 4px; width: 250px; }
.btn-primary { background-color: #42b983; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
.clickable-row { cursor: pointer; }
.clickable-row:hover { background-color: #f5f5f5; }
table { width: 100%; border-collapse: collapse; }
th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
th { background-color: #f2f2f2; }
.actions-cell { width: 180px; text-align: center; }
.actions-cell button { margin: 0 5px; padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
.btn-edit { background-color: #007bff; color: white; }
.btn-danger { background-color: #d0021b; color: white; }
h3 { margin-top: 0; }
.form-group { margin-bottom: 20px; }
.form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
.form-group input { width: 100%; padding: 10px; font-size: 1rem; border-radius: 4px; border: 1px solid #ccc; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.btn-secondary { background-color: #6c757d; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; }
.no-data, .loading-state { text-align: center; color: #666; padding: 20px; font-style: italic; }
.error { color: red; font-weight: bold; }
</style>