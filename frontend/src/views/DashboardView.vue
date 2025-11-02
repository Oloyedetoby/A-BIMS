<template>
  <div class="dashboard">
    <h2>Dashboard</h2>
    
    <div v-if="loading">Loading dashboard...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <!-- Stats Cards Section -->
    <div v-if="stats" class="stats-container">
      <div class="stat-card">
        <h3>Total Customers</h3>
        <p>{{ stats.customer_count }}</p>
      </div>
      <div class="stat-card">
        <h3>Total Books</h3>
        <p>{{ stats.book_count }}</p>
      </div>
      <div class="stat-card debtors-stat">
        <h3>Active Debtors</h3>
        <p>{{ stats.debtors_count }}</p>
      </div>
    </div>

    <!-- Debtors Danger Zone Section -->
    <div v-if="debtors.length > 0" class="debtors-zone">
      <h3><span class="danger-icon">⚠️</span> Overdue & Unpaid Invoices</h3>
      <table>
        <thead>
          <tr>
            <th>Invoice #</th>
            <th>Customer</th>
            <th>Due Date</th>
            <th>Total Amount</th>
            <th>Amount Paid</th>
            <th>Balance Due</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="debtor in debtors" :key="debtor.id">
            <td>{{ debtor.id }}</td>
            <td>{{ debtor.customer_name }}</td>
            <td>{{ debtor.due_date }}</td>
            <td>₦{{ formatPrice(debtor.total_amount) }}</td>
            <td>₦{{ formatPrice(debtor.amount_paid) }}</td>
            <td class="balance-due">₦{{ formatPrice(debtor.balance_due) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api';

const stats = ref(null);
const debtors = ref([]);
const loading = ref(true);
const error = ref(null);

onMounted(async () => {
  try {
    // Fetch both sets of data at the same time for speed
    const [statsRes, debtorsRes] = await Promise.all([
      apiClient.get('/dashboard-stats/'),
      apiClient.get('/debtors/')
    ]);
    stats.value = statsRes.data;
    debtors.value = debtorsRes.data;
  } catch (err) {
    error.value = 'Failed to fetch dashboard data.';
    console.error(err);
  } finally {
    loading.value = false;
  }
});

const formatPrice = (value) => {
    return parseFloat(value).toFixed(2);
}
</script>

<style scoped>
.stats-container {
  display: flex;
  gap: 20px;
  margin-bottom: 40px;
}
.stat-card {
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  flex-grow: 1;
  text-align: center;
}
.stat-card h3 { margin: 0 0 10px 0; color: #555; }
.stat-card p { margin: 0; font-size: 2.5rem; font-weight: bold; }
.debtors-stat p { color: #d0021b; }

.debtors-zone {
  background-color: #fff5f5;
  border: 1px solid #d0021b;
  border-radius: 8px;
  padding: 20px;
}
.debtors-zone h3 {
  color: #d0021b;
  margin: 0 0 15px 0;
}
.danger-icon { font-size: 1.5rem; }
table { width: 100%; border-collapse: collapse; }
th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
th { background-color: #ffdddd; }
.balance-due { font-weight: bold; color: #d0021b; }
</style>