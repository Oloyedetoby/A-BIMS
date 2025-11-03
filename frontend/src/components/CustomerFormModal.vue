<template>
  <!-- We reuse the generic PaymentModal component for the pop-up structure -->
  <PaymentModal :show="show" @close="$emit('close')">
    <form @submit.prevent="submitForm" class="customer-form">
      <h3>{{ isEditMode ? 'Edit Customer' : 'Add New Customer' }}</h3>
      
      <div class="form-group">
        <label for="school-name">School Name:</label>
        <input type="text" id="school-name" v-model="editableCustomer.school_name" required>
      </div>
      <div class="form-group">
        <label for="contact-person">Contact Person:</label>
        <input type="text" id="contact-person" v-model="editableCustomer.contact_person" required>
      </div>
      <div class="form-group">
        <label for="phone-number">Phone Number:</label>
        <input type="text" id="phone-number" v-model="editableCustomer.phone_number" required>
      </div>
      <div class="form-group">
        <label for="address">Address:</label>
        <textarea id="address" v-model="editableCustomer.address" required></textarea>
      </div>
      <div class="form-group">
        <label for="route-axis">Route/Axis:</label>
        <select id="route-axis" v-model="editableCustomer.route_axis_id" required>
          <option disabled value="">Select an axis</option>
          <option v-for="axis in axes" :key="axis.id" :value="axis.id">{{ axis.name }}</option>
        </select>
      </div>
      <div class="form-group">
        <label for="referred-by">Referred By (Optional):</label>
        <select id="referred-by" v-model="editableCustomer.referred_by_id">
          <option :value="null">-- None --</option>
          <option v-for="customer in potentialReferrers" :key="customer.id" :value="customer.id">
            {{ customer.school_name }}
          </option>
        </select>
      </div>

      <div class="form-actions">
        <button type="button" @click="$emit('close')" class="btn-secondary">Cancel</button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Saving...' : 'Save Customer' }}
        </button>
      </div>
      <div v-if="error" class="error">{{ error }}</div>
    </form>
  </PaymentModal>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue';
import { useToast } from 'vue-toastification';
import apiClient from '../api';
import PaymentModal from './PaymentModal.vue';

const props = defineProps({
  show: Boolean,
  customer: Object, // The customer to edit (will be null for 'create' mode)
});
const emit = defineEmits(['close', 'customer-saved']);
const toast = useToast();

const editableCustomer = ref({
  school_name: '',
  contact_person: '',
  phone_number: '',
  address: '',
  route_axis_id: '',
  referred_by_id: null,
});
const axes = ref([]);
const potentialReferrers = ref([]);
const isSubmitting = ref(false);
const error = ref(null);

const isEditMode = computed(() => !!props.customer);

// Watch for the 'customer' prop to change, then update our local editable copy
watch(() => props.customer, (newVal) => {
  if (newVal) {
    // We are in 'Edit' mode, pre-fill the form
    editableCustomer.value = { 
      ...newVal, 
      route_axis_id: newVal.route_axis?.id || '',
      referred_by_id: newVal.referred_by?.id || null 
    };
  } else {
    // We are in 'Create' mode, reset the form
    editableCustomer.value = { 
      school_name: '', contact_person: '', phone_number: '',
      address: '', route_axis_id: '', referred_by_id: null
    };
  }
});

// Fetch the data needed for the dropdowns when the component is first created
onMounted(async () => {
  try {
    const [axesRes, customersRes] = await Promise.all([
      apiClient.get('/route-axes/'),
      apiClient.get('/customers/')
    ]);
    axes.value = axesRes.data;
    potentialReferrers.value = customersRes.data;
  } catch (err) {
    toast.error("Failed to load data for the form.");
    console.error("Failed to fetch form data", err);
  }
});

const submitForm = async () => {
  isSubmitting.value = true;
  error.value = null;
  try {
    if (isEditMode.value) {
      // UPDATE (PUT) request for an existing customer
      await apiClient.put(`/customers/${props.customer.id}/`, editableCustomer.value);
      toast.success("Customer updated successfully!");
    } else {
      // CREATE (POST) request for a new customer
      await apiClient.post('/customers/', editableCustomer.value);
      toast.success("New customer added successfully!");
    }
    emit('customer-saved'); // Tell the parent component to refresh
  } catch (err) {
    error.value = 'Failed to save customer. Please check the fields.';
    toast.error(error.value);
    console.error(err);
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.customer-form h3 {
  margin-top: 0;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}
.form-group { margin-bottom: 15px; }
.form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
.form-group input, .form-group textarea, .form-group select { 
  width: 100%; 
  padding: 10px; 
  box-sizing: border-box; 
  border: 1px solid #ccc; 
  border-radius: 4px; 
  font-size: 1rem;
}
.form-actions { 
  margin-top: 25px; 
  text-align: right; 
  display: flex; 
  gap: 10px; 
  justify-content: flex-end; 
}
.btn-primary { 
  background-color: #42b983; 
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
}
.btn-primary:disabled {
  background-color: #aaa;
  cursor: not-allowed;
}
.btn-secondary { 
  background-color: #6c757d; 
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
}
.error { color: red; margin-top: 10px; text-align: right; }
</style>