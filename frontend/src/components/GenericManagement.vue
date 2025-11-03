<template>
  <div class="management-list">
    <div class="header-actions">
      <h2>{{ title }}</h2>
      <button class="btn-primary" @click="openCreateModal">+ Add New {{ singularItemName }}</button>
    </div>
    <table v-if="items.length > 0">
      <thead>
        <tr>
          <th>Name</th>
          <th class="actions-cell">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.name }}</td>
          <td class="actions-cell">
            <button class="btn-edit" @click="openEditModal(item)">Edit</button>
            <button class="btn-danger" @click="openDeleteModal(item)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else-if="!loading">No {{ itemName.toLowerCase() }} found.</p>
    <PaymentModal :show="showEditModal" @close="closeModals">
      <form @submit.prevent="submitForm">
        <h3>{{ selectedItem && selectedItem.id ? 'Edit' : 'Add New' }} {{ singularItemName }}</h3>
        <div class="form-group">
          <label>Name:</label>
          <input type="text" v-model="editableItem.name" required>
        </div>
        <div class="form-actions">
          <button type="button" @click="closeModals" class="btn-secondary">Cancel</button>
          <button type="submit" class="btn-primary">Save</button>
        </div>
      </form>
    </PaymentModal>
    <ConfirmDialog
      :show="showDeleteModal"
      :title="`Delete ${singularItemName}`"
      :message="`Are you sure you want to delete '${selectedItem?.name}'?`"
      @cancel="closeModals"
      @confirm="deleteItem"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watchEffect, computed } from 'vue';
import { useToast } from 'vue-toastification';
import apiClient from '../api';
import PaymentModal from './PaymentModal.vue';
import ConfirmDialog from './ConfirmDialog.vue';

const props = defineProps({
  title: String,
  apiEndpoint: String,
  itemName: String,
});
const singularItemName = computed(() => props.itemName.slice(0, -1));

const toast = useToast();
const items = ref([]);
const loading = ref(true);
const showEditModal = ref(false);
const showDeleteModal = ref(false);
const selectedItem = ref(null);
const editableItem = ref({ name: '' });

const fetchData = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get(`/${props.apiEndpoint}/`);
    items.value = response.data;
  } catch (err) {
    toast.error(`Failed to fetch ${props.itemName.toLowerCase()}.`);
  } finally {
    loading.value = false;
  }
};
onMounted(fetchData);

watchEffect(() => {
  editableItem.value = selectedItem.value ? { ...selectedItem.value } : { name: '' };
});

const closeModals = () => { showEditModal.value = false; showDeleteModal.value = false; selectedItem.value = null; };
const handleSave = () => { closeModals(); fetchData(); };

const openCreateModal = () => { selectedItem.value = null; showEditModal.value = true; };
const openEditModal = (item) => { selectedItem.value = item; showEditModal.value = true; };
const openDeleteModal = (item) => { selectedItem.value = item; showDeleteModal.value = true; };

const submitForm = async () => {
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
    toast.error(`Failed to save ${singularItemName.value.toLowerCase()}.`);
  }
};

const deleteItem = async () => {
  try {
    await apiClient.delete(`/${props.apiEndpoint}/${selectedItem.value.id}/`);
    toast.success(`${singularItemName.value} deleted successfully.`);
    handleSave();
  } catch (err) {
    toast.error(`Failed to delete ${singularItemName.value.toLowerCase()}. It may be in use.`);
  }
};
</script>
<style scoped>
/* Styling from AuthorsView.vue will work perfectly here */
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
.form-group { margin-bottom: 20px; }
.form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
.form-group input { width: 100%; padding: 10px; font-size: 1rem; border-radius: 4px; border: 1px solid #ccc; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.btn-secondary { background-color: #6c757d; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; }
</style>