<template>
  <div>
    <div v-if="loading">Loading receipt...</div>
    <div v-if="error" class="error">{{ error }}</div>
    <Receipt v-if="payment && invoice" :payment="payment" :invoice="invoice" />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '../api';
import Receipt from '../components/Receipt.vue';

const route = useRoute();
const payment = ref(null);
const invoice = ref(null);
const loading = ref(true);
const error = ref(null);

onMounted(async () => {
  const invoiceId = route.params.invoiceId;
  const paymentId = route.params.paymentId;
  try {
    // We need to fetch both the invoice and the specific payment
    // We'll need a new API endpoint to get a single payment
    const invoiceRes = await apiClient.get(`/invoices/${invoiceId}/`);
    // For simplicity, we find the payment from the invoice's payment list
    const foundPayment = invoiceRes.data.payments.find(p => p.id == paymentId);
    
    if (foundPayment) {
      invoice.value = invoiceRes.data;
      payment.value = foundPayment;
      
      // Wait for Vue to render the component, then print
      await nextTick();
      window.print();
    } else {
      error.value = "Payment not found.";
    }
  } catch (err) {
    error.value = "Failed to load receipt data.";
  } finally {
    loading.value = false;
  }
});
</script>