<template>
  <div>
    <div v-if="loading">Loading customer details...</div>
    <div v-if="error" class="error">{{ error }}</div>
    
    <div v-if="customer" class="customer-dashboard">
      <!-- Header Section -->
      <div class="customer-header">
        <h1>{{ customer.school_name }}</h1>
        <div class="header-actions">
          <button class="btn-primary" @click="showEditModal = true">Edit Customer</button>
          <button class="btn-danger" @click="showDeleteModal = true">Delete Customer</button>
        </div>
      </div>

      <!-- Summary Cards Section -->
      <div v-if="customerStats" class="stats-container">
        <div class="stat-card">
          <h3>Total Invoiced</h3>
          <p>₦{{ formatPrice(customerStats.totalInvoiced) }}</p>
        </div>
        <div class="stat-card">
          <h3>Total Paid</h3>
          <p>₦{{ formatPrice(customerStats.totalPaid) }}</p>
        </div>
        <div class="stat-card balance">
          <h3>Outstanding Balance</h3>
          <p>₦{{ formatPrice(customerStats.outstandingBalance) }}</p>
        </div>
        <div class="stat-card">
          <h3>Referrals Made</h3>
          <p>{{ customer.referred_customers?.length ?? 0 }}</p>
        </div>
      </div>

      <!-- Details Section -->
      <div class="details-section">
        <h3>Customer Details</h3>
        <p><strong>Contact Person:</strong> {{ customer.contact_person }}</p>
        <p><strong>Phone Number:</strong> {{ customer.phone_number }}</p>
        <p><strong>Route/Axis:</strong> {{ customer.route_axis }}</p>
        <p><strong>Address:</strong> {{ customer.address }}</p>
        <p v-if="customer.referred_by"><strong>Referred By:</strong> {{ customer.referred_by.school_name }}</p>
      </div>

      <!-- Referrals Made Section -->
      <div v-if="customer.referred_customers && customer.referred_customers.length > 0" class="referrals-section">
        <h3>Customers Referred by {{ customer.school_name }}</h3>
        <ul>
          <li v-for="referred in customer.referred_customers" :key="referred.id">
            <router-link :to="{ name: 'CustomerDetail', params: { id: referred.id } }">
              {{ referred.school_name }} ({{ referred.route_axis }})
            </router-link>
          </li>
        </ul>
      </div>

      <!-- Invoice History Section -->
      <div class="invoice-history">
        <h3>Invoice History</h3>
        <div v-if="customer.invoices?.length > 0">
          <div v-for="invoice in customer.invoices" :key="invoice.id" class="invoice-card" :class="getInvoiceStatusClass(invoice.status)">
            <div class="invoice-header">
              <h4>Invoice #{{ invoice.id }} ({{ invoice.invoice_date }})</h4>
              <div class="invoice-actions">
                <button class="btn-return" @click="openCreditNoteModal(invoice)">Return/Credit</button>
                <span class="status" :class="getInvoiceStatusClass(invoice.status)">{{ invoice.status.replace('_', ' ') }}</span>
              </div>
            </div>
            <div class="financial-summary">
              <p>Total: <span>₦{{ formatPrice(invoice.total_amount) }}</span></p>
              <p>Paid: <span>₦{{ formatPrice(invoice.amount_paid) }}</span></p>
              <p class="balance-due">Balance: <span>₦{{ formatPrice(invoice.balance_due) }}</span></p>
            </div>
          </div>
        </div>
        <p v-else>This customer has no invoice history.</p>
      </div>
    </div>

    <!-- The Edit Customer Modal -->
    <CustomerFormModal 
      :show="showEditModal" 
      :customer="customer"
      @close="showEditModal = false"
      @customer-saved="handleCustomerSaved"
    />

    <!-- The Delete Confirmation Dialog -->
    <ConfirmDialog 
      :show="showDeleteModal"
      title="Delete Customer"
      :message="`Are you sure you want to delete ${customer?.school_name}? All associated invoices will also be deleted. This cannot be undone.`"
      @cancel="showDeleteModal = false"
      @confirm="deleteCustomer"
    />

    <!-- The New Credit Note Modal -->
    <CreditNoteFormModal
      :show="showCreditNoteModal"
      :invoice="selectedInvoiceForCredit"
      @close="showCreditNoteModal = false"
      @credit-note-saved="handleCreditNoteSaved"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import apiClient from '../api';
import CustomerFormModal from '../components/CustomerFormModal.vue';
import ConfirmDialog from '../components/ConfirmDialog.vue';
import CreditNoteFormModal from '../components/CreditNoteFormModal.vue';

const route = useRoute();
const router = useRouter();
const toast = useToast();

const customer = ref(null);
const loading = ref(true);
const error = ref(null);
const showEditModal = ref(false);
const showDeleteModal = ref(false);
const showCreditNoteModal = ref(false);
const selectedInvoiceForCredit = ref(null);

// --- API Calls & Actions ---
const fetchCustomerData = async () => {
  loading.value = true;
  const customerId = route.params.id;
  try {
    const response = await apiClient.get(`/customers/${customerId}/`);
    customer.value = response.data;
  } catch (err) {
    error.value = 'Failed to fetch customer details.';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const deleteCustomer = async () => {
  if (!customer.value) return;
  try {
    await apiClient.delete(`/customers/${customer.value.id}/`);
    toast.success(`Customer "${customer.value.school_name}" deleted successfully.`);
    showDeleteModal.value = false;
    router.push('/customers'); // Navigate back to the customer list
  } catch (err) {
    toast.error("Failed to delete customer.");
    console.error(err);
  }
};

onMounted(fetchCustomerData);

// --- Event Handlers ---
const handleCustomerSaved = () => {
  showEditModal.value = false;
  fetchCustomerData(); // Re-fetch the data to show the latest updates
};

const openCreditNoteModal = (invoice) => {
  // This is the fix: Attach the main customer object to the selected invoice
  selectedInvoiceForCredit.value = { ...invoice, customer: customer.value };
  showCreditNoteModal.value = true;
};

const handleCreditNoteSaved = () => {
  showCreditNoteModal.value = false;
  fetchCustomerData(); // Refresh all data to see updated balances
};

// --- Computed Properties for Stats ---
const customerStats = computed(() => {
  if (!customer.value || !customer.value.invoices) {
    return { totalInvoiced: 0, totalPaid: 0, outstandingBalance: 0 };
  }
  const totalInvoiced = customer.value.invoices?.reduce((sum, inv) => sum + parseFloat(inv.total_amount || 0), 0);
  const totalPaid = customer.value.invoices?.reduce((sum, inv) => sum + parseFloat(inv.amount_paid || 0), 0);
  const outstandingBalance = totalInvoiced - totalPaid;
  
  return { totalInvoiced, totalPaid, outstandingBalance };
});

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
</script>

<style scoped>
.customer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 20px;
}
.customer-header h1 { margin: 0; }
.header-actions {
  display: flex;
  gap: 10px;
}
.btn-primary { 
  background-color: #007bff; 
  color: white; 
  padding: 8px 15px; 
  border: none; 
  border-radius: 5px; 
  cursor: pointer;
  font-size: 0.9rem;
}
.btn-danger {
  background-color: #d0021b;
  color: white;
  padding: 8px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9rem;
}

.stats-container { display: flex; gap: 20px; margin-bottom: 30px; }
.stat-card { background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 8px; padding: 20px; flex-grow: 1; text-align: center; }
.stat-card h3 { margin: 0 0 10px 0; font-size: 1rem; color: #555; }
.stat-card p { margin: 0; font-size: 2rem; font-weight: bold; }
.stat-card.balance p { color: #d0021b; }

.details-section, .invoice-history, .referrals-section {
  background-color: #fdfdfd;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
}
.details-section h3, .invoice-history h3, .referrals-section h3 {
  margin-top: 0;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}
.details-section p { font-size: 1rem; margin: 8px 0; }

.invoice-card { border: 1px solid #ddd; border-left-width: 4px; border-radius: 5px; margin-bottom: 10px; padding: 15px; }
.invoice-card.unpaid { border-left-color: #d0021b; }
.invoice-card.paid { border-left-color: #42b983; }
.invoice-card.partiallypaid { border-left-color: #f5a623; }

.invoice-header { display: flex; justify-content: space-between; align-items: center; padding: 0; border: none; margin-bottom: 10px; }
.invoice-header h4 { margin: 0; font-size: 1.1rem; }
.invoice-actions { display: flex; align-items: center; gap: 10px; }
.btn-return { background: none; border: 1px solid #ffc107; color: #ad8b21; padding: 4px 8px; font-size: 0.75rem; border-radius: 4px; cursor: pointer; font-weight: bold; }
.btn-return:hover { background-color: #fff8e1; }
.status { padding: 4px 8px; border-radius: 12px; font-size: 0.75rem; }

.financial-summary { text-align: right; font-size: 0.9rem; }
.financial-summary p { margin: 2px 0; }
.financial-summary span { font-weight: bold; display: inline-block; min-width: 80px; text-align: left;}

.referrals-section ul { list-style-type: none; padding-left: 0; }
.referrals-section li { padding: 8px 0; border-bottom: 1px solid #eee; }
.referrals-section li:last-child { border-bottom: none; }
.referrals-section a { text-decoration: none; color: #007bff; font-weight: bold; }
.referrals-section a:hover { text-decoration: underline; }

.error { color: red; font-weight: bold; }
</style>