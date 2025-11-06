<template>
  <div class="insights-page">
    <h1>Business Insights</h1>
    
    <div v-if="loading">Loading insights...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="insights" class="insights-grid">
      <!-- Highest Debtors -->
      <div class="insight-card">
        <h3>Top 3 Highest Debtors</h3>
        <ol>
          <li v-for="debtor in insights.highest_debtors" :key="debtor.name">
            <span>{{ debtor.name }}</span>
            <span class="value">₦{{ formatPrice(debtor.balance) }}</span>
          </li>
        </ol>
      </div>

      <!-- Best Customers -->
      <div class="insight-card">
        <h3>Top 3 Best Customers (by Total Paid)</h3>
        <ol>
          <li v-for="customer in insights.best_customers" :key="customer.name">
            <span>{{ customer.name }}</span>
            <span class="value">₦{{ formatPrice(customer.total_spent) }}</span>
          </li>
        </ol>
      </div>

      <!-- Best Selling Books -->
      <div class="insight-card">
        <h3>Top 3 Best-Selling Books (by Revenue)</h3>
        <ol>
          <li v-for="book in insights.best_selling_books" :key="book.title">
            <span>{{ book.title }}</span>
            <span class="value">₦{{ formatPrice(book.revenue) }}</span>
          </li>
        </ol>
      </div>

      <!-- Most Stocked -->
      <div class="insight-card">
        <h3>Top 3 Most Stocked Books</h3>
        <ol>
          <li v-for="book in insights.most_stocked_books" :key="book.title">
            <span>{{ book.title }}</span>
            <span class="value">{{ book.quantity_in_stock }} units</span>
          </li>
        </ol>
      </div>

      <!-- Lowest Stocked -->
      <div class="insight-card low-stock">
        <h3>Top 3 Lowest Stocked Books</h3>
        <ol>
          <li v-for="book in insights.lowest_stocked_books" :key="book.title">
            <span>{{ book.title }}</span>
            <span class="value">{{ book.quantity_in_stock }} units</span>
          </li>
        </ol>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api';

const insights = ref(null);
const loading = ref(true);
const error = ref(null);

onMounted(async () => {
  try {
    const response = await apiClient.get('/insights/');
    insights.value = response.data;
  } catch (err) {
    error.value = "Failed to load business insights.";
    console.error(err);
  } finally {
    loading.value = false;
  }
});

const formatPrice = (value) => {
  const num = parseFloat(value);
  return isNaN(num) ? '0.00' : num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
};
</script>

<style scoped>
.insights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}
.insight-card {
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
}
.insight-card h3 {
  margin-top: 0;
  border-bottom: 1px solid #ccc;
  padding-bottom: 10px;
}
.insight-card ol {
  list-style-type: none;
  padding-left: 0;
}
.insight-card li {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}
.insight-card li:last-child {
  border-bottom: none;
}
.insight-card .value {
  font-weight: bold;
}
.low-stock {
  border-left: 5px solid #d0021b;
}
.low-stock .value {
    color: #d0021b;
}
</style>