<template>
  <div class="invoice-list">
    <div class="header-actions">
      <h2>Invoices</h2>
        
      <select v-model="selectedStatus" @change="fetchInvoices">
        <option value="">All Statuses</option>
        <option value="UNPAID">Unpaid</option>
        <option value="PARTIALLY_PAID">Partially Paid</option>
        <option value="PAID">Paid</option>
      </select>
      <router-link to="/invoices/new" class="btn-primary">Create New Invoice</router-link>
    </div>
    
    <div v-if="loading">Loading invoices...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="invoices.length > 0" class="invoices-container">
      <div v-for="invoice in invoices" :key="invoice.id" class="invoice-card" :class="getInvoiceStatusClass(invoice.status)">
        <div class="invoice-header">
           <h3>Invoice #{{ invoice.id }} - {{ invoice.customer_name }}</h3>
           <span class="status" :class="getInvoiceStatusClass(invoice.status)">{{ invoice.status.replace('_', ' ') }}</span>
        </div>
        <div class="invoice-details">
          <p><strong>Date:</strong> {{ invoice.invoice_date }}</p>
          <p><strong>Due Date:</strong> {{ invoice.due_date }}</p>
        </div>
        
        <h4>Items:</h4>
        <table>
          <thead>
            <tr>
              <th>Book</th>
              <th>Quantity</th>
              <th>Unit Price</th>
              <th>Subtotal</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in invoice.items" :key="item.id">
              <td>{{ item.book }}</td>
              <td>{{ item.quantity }}</td>
              <td>₦{{ formatPrice(item.unit_price) }}</td>
              <td>₦{{ formatPrice(item.quantity * item.unit_price) }}</td>
            </tr>
          </tbody>
        </table>
        
        <div class="financial-summary">
          <p>Total Amount: <span>₦{{ formatPrice(invoice.total_amount) }}</span></p>
          <p class="credit" v-if="invoice.credit_applied > 0">Credit Applied: <span>- ₦{{ formatPrice(invoice.credit_applied) }}</span></p>
          <p>Amount Paid: <span>₦{{ formatPrice(invoice.amount_paid) }}</span></p>
          <p class="balance-due">Balance Due: <span>₦{{ formatPrice(invoice.balance_due) }}</span></p>
        </div>

        <div v-if="invoice.payments && invoice.payments.length > 0" class="payment-history">
          <h5>Payment History:</h5>
          <table class="payment-table">
            <tbody>
              <tr v-for="payment in invoice.payments" :key="payment.id">
                <td>Payment on {{ payment.payment_date }}</td>
                <td class="notes">{{ payment.notes }}</td>
                <td>₦{{ formatPrice(payment.amount) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div class="card-actions" v-if="invoice.status !== 'PAID'">
          <button class="btn-secondary" @click="openPaymentModal(invoice)">Record Payment</button>
        </div>
      </div>
    </div>
    <div v-else-if="!loading" class="no-invoices">
      <p>No invoices found. Why not create one?</p>
    </div>

    <!-- Payment Modal Component -->
    <PaymentModal :show="showModal" @close="closePaymentModal">
      <div v-if="selectedInvoice">
        <h3>Record Payment for Invoice #{{ selectedInvoice.id }}</h3>
        <p><strong>Balance Due:</strong> ₦{{ formatPrice(selectedInvoice.balance_due) }}</p>
        <form @submit.prevent="submitPayment">
          <div class="form-group">
            <label for="payment-amount">Amount:</label>
            <input type="number" id="payment-amount" v-model.number="paymentData.amount" step="0.01" required>
          </div>
          <div class="form-group">
            <label for="payment-notes">Notes (Optional):</label>
            <textarea id="payment-notes" v-model="paymentData.notes" placeholder="e.g., Bank Transfer"></textarea>
          </div>
          <button type="submit" :disabled="isSubmitting" class="btn-primary">
            {{ isSubmitting ? 'Saving...' : 'Save Payment' }}
          </button>
          <div v-if="paymentError" class="error">{{ paymentError }}</div>
        </form>
      </div>
    </PaymentModal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useToast } from 'vue-toastification';
import apiClient from '../api';
import PaymentModal from '../components/PaymentModal.vue';

// --- Reactive State ---
const invoices = ref([]);
const loading = ref(true);
const error = ref(null);

const showModal = ref(false);
const selectedInvoice = ref(null);
const isSubmitting = ref(false);
const paymentError = ref(null);
const paymentData = ref({
  amount: 0,
  notes: ''
});
const toast = useToast();
const selectedStatus = ref('');

// --- API Calls ---
const fetchInvoices = async () => {
  loading.value = true;
  error.value = null;
  try {
    const params = {};
    if (selectedStatus.value) {
      params.status = selectedStatus.value;
    }

    const response = await apiClient.get('/invoices/', { params });  

    invoices.value = response.data;
  } catch (err) {
    error.value = 'Failed to fetch invoices. Please check the backend server and the browser console for errors.';
    console.error("Error fetching invoices:", err);
  } finally {
    loading.value = false;
  }
};

const submitPayment = async () => {
  if (!selectedInvoice.value) return;
  isSubmitting.value = true;
  paymentError.value = null;
  try {
    const url = `/invoices/${selectedInvoice.value.id}/record_payment/`;
    await apiClient.post(url, paymentData.value);
    
    toast.success("Payment recorded successfully!");
    closePaymentModal();
    await fetchInvoices();
  } catch (err) {
    toast.error("Failed to record payment. Please try again.");
    paymentError.value = 'Failed to record payment.';
    console.error("Error submitting payment:", err);
  } finally {
    isSubmitting.value = false;
  }
};

// --- Modal Controls ---
const openPaymentModal = (invoice) => {
  selectedInvoice.value = invoice;
  paymentData.value.amount = invoice.balance_due;
  paymentData.value.notes = '';
  paymentError.value = null;
  showModal.value = true;
};

const closePaymentModal = () => {
  showModal.value = false;
  selectedInvoice.value = null;
};

// --- Helper Functions ---
const formatPrice = (value) => {
  const num = parseFloat(value);
  if (isNaN(num)) return '0.00';
  return num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
};

const getInvoiceStatusClass = (status) => {
    if (!status) return '';
    return status.toLowerCase().replace('_', '');
}

// --- Lifecycle Hook ---
onMounted(fetchInvoices);
</script>

<style scoped>
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.filters {
  display: flex;
  gap: 15px;
  align-items: center;
}

.filters select {
  padding: 8px 12px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: white;
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
.btn-primary:disabled {
    background-color: #aaa;
    cursor: not-allowed;
}

.invoice-card {
  background-color: #fff;
  border: 1px solid #ddd;
  border-left-width: 5px;
  border-radius: 5px;
  margin-bottom: 20px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.invoice-card.unpaid { border-left-color: #d0021b; }
.invoice-card.paid { border-left-color: #42b983; }
.invoice-card.partiallypaid { border-left-color: #f5a623; }

.invoice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}
.invoice-header h3 {
  margin: 0;
}
.status {
  padding: 5px 10px;
  border-radius: 15px;
  color: white;
  font-weight: bold;
  font-size: 0.8rem;
  text-transform: capitalize;
}
.status.unpaid { background-color: #d0021b; }
.status.paid { background-color: #42b983; }
.status.partiallypaid { background-color: #f5a623; }

.invoice-details {
  margin-bottom: 15px;
  color: #555;
  font-size: 0.9rem;
}
.invoice-details p {
  margin: 4px 0;
}

table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.9rem; }
th, td { border: 1px solid #eee; padding: 8px; }
th { background-color: #f9f9f9; text-align: left; }

.financial-summary {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
  text-align: right;
}
.financial-summary p {
  margin: 5px 0;
  font-size: 1rem;
}
.financial-summary span {
  display: inline-block;
  min-width: 120px;
  font-weight: bold;
  text-align: left;
}
.financial-summary .credit span {
    color: #007bff;
}
.financial-summary .balance-due {
  font-size: 1.2rem;
  font-weight: bold;
}
.financial-summary .balance-due span {
    color: #d0021b;
}

.payment-history {
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px dashed #ccc;
  font-size: 0.9rem;
}
.payment-history h5 {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 0.9rem;
  text-align: left;
}
.payment-table {
  width: 100%;
  font-size: 0.85rem;
}
.payment-table td {
  border: none;
  padding: 4px 8px;
  color: #555;
}
.payment-table .notes {
    color: #777;
    font-style: italic;
    text-align: left;
}
.payment-table td:last-child {
  text-align: right;
  font-weight: bold;
  min-width: 100px;
}

.card-actions { margin-top: 20px; text-align: right; }
.btn-secondary { background-color: #007bff; color: white; padding: 8px 12px; border: none; border-radius: 5px; cursor: pointer; }

.form-group { margin-bottom: 15px; }
.form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
.form-group input, .form-group textarea { width: 100%; padding: 10px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }

.no-invoices {
    text-align: center;
    padding: 40px;
    color: #777;
}

.error { color: red; font-weight: bold; margin-top: 10px; }
</style>