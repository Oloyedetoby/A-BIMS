<template>
  <div class="customer-list">
    <div class="header-actions">
      <h2>Customer List</h2>
      <div class="filters">
        <!-- NEW: The Route/Axis filter dropdown -->
        <select v-model="selectedAxis" @change="fetchCustomers">
          <option value="">All Route/Axes</option>
          <option v-for="axis in axes" :key="axis.id" :value="axis.id">
            {{ axis.name }}
          </option>
        </select>
        
        <!-- The search bar -->
        <input 
          type="text" 
          v-model="searchTerm" 
          placeholder="Search customers..."
          @input="fetchCustomers"
        >
      </div>
    </div>

    <div v-if="loading">Loading customers...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <table v-if="customers.length > 0">
      <!-- table content is the same -->
      <thead>
        <tr>
          <th>School Name</th>
          <th>Route/Axis</th>
          <th>Contact Person</th>
          <th>Phone Number</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="customer in customers" :key="customer.id">
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api';

// --- Reactive State ---
const customers = ref([]);
const loading = ref(true);
const error = ref(null);
const searchTerm = ref('');

// NEW: State for the filter dropdown
const axes = ref([]);
const selectedAxis = ref('');

// --- API Calls ---
const fetchCustomers = async () => {
  loading.value = true;
  error.value = null;
  try {
    // Build parameters for the API call
    const params = {};
    if (searchTerm.value) {
      params.search = searchTerm.value;
    }
    // NEW: Add the selected axis to the parameters
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

// NEW: Function to fetch the list of available axes for the dropdown
const fetchAxes = async () => {
    try {
        // We need an API endpoint for this. We will create it.
        const response = await apiClient.get('/route-axes/');
        axes.value = response.data;
    } catch (err) {
        console.error("Failed to fetch route axes:", err);
    }
};

// --- Lifecycle Hook ---
onMounted(() => {
  // Fetch both the customer list and the axis list when the page loads
  fetchCustomers();
  fetchAxes();
});
</script>

<style scoped>
/* Update styling to accommodate multiple filters */
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
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

/* ... other styles are the same ... */
table { width: 100%; border-collapse: collapse; margin-top: 20px; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
th { background-color: #f2f2f2; }
.error { color: red; font-weight: bold; }
</style>