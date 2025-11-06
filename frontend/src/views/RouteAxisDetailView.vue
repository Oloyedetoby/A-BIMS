<template>
  <div>
    <div v-if="loading">Loading axis details...</div>
    <div v-if="error" class="error">{{ error }}</div>
    
    <div v-if="axis">
      <h1>{{ axis.name }} Axis</h1>
      
      <div class="customers-section">
        <h3>Customers in this Axis ({{ axis.customers.length }})</h3>
        <div v-if="axis.customers && axis.customers.length > 0">
          <table>
            <thead>
              <tr>
                <th>School Name</th>
                <th>Contact Person</th>
                <th>Phone Number</th>
              </tr>
            </thead>
            <tbody>
              <!-- The rows are clickable, linking to the Customer Detail page -->
              <tr v-for="customer in axis.customers" :key="customer.id" @click="viewCustomer(customer.id)" class="clickable-row">
                <td>{{ customer.school_name }}</td>
                <td>{{ customer.contact_person }}</td>
                <td>{{ customer.phone_number }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else>There are no customers assigned to this axis yet.</p>
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
const axis = ref(null);
const loading = ref(true);
const error = ref(null);

onMounted(async () => {
  const axisId = route.params.id;
  try {
    const response = await apiClient.get(`/route-axes/${axisId}/`);
    axis.value = response.data;
  } catch (err) {
    error.value = 'Failed to fetch axis details.';
    console.error(err);
  } finally {
    loading.value = false;
  }
});

const viewCustomer = (customerId) => {
  router.push({ name: 'CustomerDetail', params: { id: customerId } });
};
</script>

<style scoped>
h1 { border-bottom: 1px solid #eee; padding-bottom: 15px; }
.customers-section { margin-top: 30px; }
table { width: 100%; border-collapse: collapse; margin-top: 15px; }
th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
th { background-color: #f2f2f2; }
.clickable-row { cursor: pointer; }
.clickable-row:hover { background-color: #f5f5f5; }
</style>