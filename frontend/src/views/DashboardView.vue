<template>
  <div class="dashboard">
    <h2>Dashboard</h2>
    
    <div v-if="loading" class="loading-state">Loading dashboard...</div>
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
    <div v-if="!loading && debtors.length > 0" class="debtors-zone">
      <h3><span class="danger-icon">⚠️</span> Overdue & Unpaid Invoices</h3>
      <table>
        <thead>
          <tr>
            <th>Invoice #</th>
            <th>Customer</th>
            <th @click="sortBy('due_date')" class="sortable">
              Due Date <span v-if="sortField === 'due_date'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span>
            </th>
            <th class="text-center">Days Overdue</th>
            <th @click="sortBy('balance_due')" class="sortable text-right">
              Balance Due <span v-if="sortField === 'balance_due'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="debtor in debtors" :key="debtor.id">
            <td @click="viewInvoice(debtor.id)" class="link-cell">#{{ debtor.id }}</td>
            <td @click="viewCustomer(debtor.customer_id)" class="link-cell">{{ debtor.customer_name }}</td>
            <td>{{ debtor.due_date }}</td>
            <td class="text-center" :class="getOverdueClass(debtor.days_overdue)">
              {{ debtor.days_overdue }}
            </td>
            <td class="balance-due text-right">₦{{ formatPrice(debtor.balance_due) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="!loading" class="no-debtors">
        <p>🎉 No outstanding debts found. Great job!</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../api';

const router = useRouter();
const stats = ref(null);
const debtors = ref([]);
const loading = ref(true);
const error = ref(null);

// State for sorting
const sortField = ref('due_date'); // Default sort field
const sortDir = ref('asc'); // Default sort direction

const fetchDebtors = async () => {
  try {
    const orderingParam = `${sortDir.value === 'desc' ? '-' : ''}${sortField.value}`;
    const response = await apiClient.get('/debtors/', {
      params: { ordering: orderingParam }
    });
    debtors.value = response.data;
  } catch (err) {
    error.value = 'Failed to fetch debtors list.';
    console.error(err);
  }
};

const fetchStats = async () => {
    try {
        const response = await apiClient.get('/dashboard-stats/');
        stats.value = response.data;
    } catch (err) {
        error.value = 'Failed to fetch dashboard stats.';
        console.error(err);
    }
};

onMounted(async () => {
  loading.value = true;
  await Promise.all([
    fetchStats(),
    fetchDebtors()
  ]);
  loading.value = false;
});

const sortBy = (field) => {
  if (sortField.value === field) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortField.value = field;
    sortDir.value = field === 'balance_due' ? 'desc' : 'asc';
  }
  fetchDebtors(); // Re-fetch the data with the new sort order
};

const formatPrice = (value) => {
    const num = parseFloat(value);
    return isNaN(num) ? '0.00' : num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
};

const getOverdueClass = (days) => {
  if (days > 30) return 'overdue-critical';
  if (days > 7) return 'overdue-warning';
  if (days > 0) return 'overdue-ok';
  return '';
};

const viewCustomer = (customerId) => {
  router.push({ name: 'CustomerDetail', params: { id: customerId } });
};

const viewInvoice = (invoiceId) => {
  router.push('/invoices');
};
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
th, td { border-bottom: 1px solid #ddd; padding: 12px; text-align: left; }
th { background-color: #ffdddd; }
td { background-color: #fff; }
tr:last-child td { border-bottom: none; }

.sortable {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s;
}
.sortable:hover {
  background-color: #f5c7c7;
}
.sortable span {
  font-size: 0.8em;
  padding-left: 5px;
}

.text-right { text-align: right; }
.text-center { text-align: center; }

.balance-due { font-weight: bold; color: #d0021b; }

.link-cell {
  cursor: pointer;
  color: #007bff;
  font-weight: 500;
}
.link-cell:hover {
  text-decoration: underline;
  background-color: #f8f9fa;
}

.overdue-ok { font-weight: bold; color: #ffc107; }
.overdue-warning { font-weight: bold; color: #fd7e14; }
.overdue-critical { font-weight: bold; color: #d0021b; background-color: #ffe8e8; }
.no-debtors { text-align: center; padding: 30px; font-size: 1.2rem; color: #28a745; background-color: #f0fff4; border: 1px solid #28a745; border-radius: 8px; }
.loading-state, .error { text-align: center; padding: 20px; font-style: italic; }
.error { color: red; font-weight: bold; }
</style>