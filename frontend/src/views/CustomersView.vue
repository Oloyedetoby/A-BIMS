<template>
  <div class="customer-list">
    <div class="header-actions">
      <h2>Customer List</h2>
      <div class="controls">
        <button class="btn-primary" @click="openCreateModal">+ Add New Customer</button>
        <div class="filters">
          <select v-model="selectedAxis" @change="fetchCustomers">
            <option value="">All Route/Axes</option>
            <option v-for="axis in axes" :key="axis.id" :value="axis.id">
              {{ axis.name }}
            </option>
          </select>
          
          <input 
            type="text" 
            v-model="searchTerm" 
            placeholder="Search customers..."
            @input="debouncedFetchCustomers"
          >
        </div>
      </div>
    </div>

    <div v-if="loading">Loading customers...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <table v-if="customers.length > 0">
      <thead>
        <tr>
          <th>School Name</th>
          <th>Route/Axis</th>
          <th>Contact Person</th>
          <th>Phone Number</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="customer in customers" 
            :key="customer.id" 
            @click="viewCustomer(customer.id)" 
            class="clickable-row">
          <td>{{ customer.school_name }}</td>
          <td>{{ customer.route_axis }}</td>
          <td>{{ customer.contact_person }}</td>
          <td>{{ customer.phone_number }}</td>
        </tr>
      </tbody>
    </table>
    <div v-else-if="!loading">
        <p>No customers found matching your criteria.</p>
    </div>

    <!-- The Modal for Creating (and Editing) Customers -->
    <CustomerFormModal 
      :show="showModal" 
      :customer="null"  
      @close="showModal = false"
      @customer-saved="handleCustomerSaved"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../api';
import CustomerFormModal from '../components/CustomerFormModal.vue';

// --- Reactive State ---
const router = useRouter();
const customers = ref([]);
const loading = ref(true);
const error = ref(null);
const searchTerm = ref('');
const axes = ref([]);
const selectedAxis = ref('');
let debounceTimer = null;

// State for the modal
const showModal = ref(false);

// --- Navigation ---
const viewCustomer = (customerId) => {
  router.push(`/customers/${customerId}`);
};

// --- Modal Controls ---
const openCreateModal = () => {
  showModal.value = true;
};

const handleCustomerSaved = () => {
  showModal.value = false;
  fetchCustomers(); // Refresh the customer list to show the new entry
};

// --- API Calls ---
const fetchCustomers = async () => {
  loading.value = true;
  error.value = null;
  try {
    const params = {};
    if (searchTerm.value) {
      params.search = searchTerm.value;
    }
    if (selectedAxis.value) {
      params.route_axis = selectedAxis.value;
    }
    
    const response = await apiClient.get('/customers/', { params });
    customers.value = response.data;
  } catch (err) {
    error.value = 'Failed to fetch customers.';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const fetchAxes = async () => {
    try {
        const response = await apiClient.get('/route-axes/');
        axes.value = response.data;
    } catch (err) {
        console.error("Failed to fetch route axes:", err);
    }
};

// Debounce the search input to avoid excessive API calls
const debouncedFetchCustomers = () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        fetchCustomers();
    }, 300); // Wait for 300ms of inactivity before fetching
};

// --- Lifecycle Hook ---
onMounted(() => {
  fetchCustomers();
  fetchAxes();
});
</script>

<style scoped>
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.controls {
  display: flex;
  gap: 15px;
  align-items: center;
}
.btn-primary {
  background-color: #42b983;
  color: white;
  padding: 10px 15px;
  text-decoration: none;
  border-radius: 5px;
  font-weight: bold;
  border: none;
  cursor: pointer;
}

.clickable-row {
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.clickable-row:hover {
  background-color: #f5f5f5;
}

.filters {
  display: flex;
  gap: 15px;
}

.filters input, .filters select {
  padding: 8px 12px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.filters input {
  width: 300px;
}

table { 
  width: 100%; 
  border-collapse: collapse; 
  margin-top: 20px; 
}
th, td { 
  border: 1px solid #ddd; 
  padding: 12px; 
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