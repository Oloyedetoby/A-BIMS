<template>
  <div class="create-invoice">
    <h2>Create New Invoice</h2>
    <form @submit.prevent="submitInvoice" class="invoice-form">
      <!-- Customer Selection -->
      <div class="form-section">
        <h3>1. Select Customer</h3>
        <select v-model="invoice.customer_id" required>
          <option disabled value="">Please select a customer</option>
          <option v-for="customer in customers" :key="customer.id" :value="customer.id">
            {{ customer.school_name }} ({{ customer.route_axis }})
          </option>
        </select>
      </div>

      <!-- Invoice Details -->
      <div class="form-section">
        <h3>2. Set Details</h3>
        <div class="details-grid">
          <div>
            <label for="due-date">Due Date:</label>
            <input type="date" id="due-date" v-model="invoice.due_date" required />
          </div>
          <div>
            <label for="status">Status:</label>
            <select id="status" v-model="invoice.status">
              <option value="UNPAID">Unpaid</option>
              <option value="PAID">Paid</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Add Line Items -->
      <div class="form-section">
        <h3>3. Add Books</h3>
        <div class="add-item-form">
          <select v-model="newItem.book_id">
            <option disabled value="">Select a book</option>
            <option v-for="book in books" :key="book.id" :value="book.id">
              {{ book.title }} - (₦{{ book.price }})
            </option>
          </select>
          <input type="number" v-model.number="newItem.quantity" placeholder="Qty" min="1" class="qty-input">
          <button type="button" @click="addItem" class="btn-secondary">Add Item</button>
        </div>
      </div>

      <!-- Items Table -->
      <div v-if="invoice.items.length > 0" class="items-table">
        <h3>Invoice Items</h3>
        <table>
          <thead>
            <tr>
              <th>Book</th>
              <th>Quantity</th>
              <th>Unit Price</th>
              <th>Subtotal</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in invoice.items" :key="index">
              <td>{{ getBookDetails(item.book_id).title }}</td>
              <td>{{ item.quantity }}</td>
              <td>₦{{ formatPrice(getBookDetails(item.book_id).price) }}</td>
              <td>₦{{ formatPrice(item.quantity * getBookDetails(item.book_id).price) }}</td>
              <td><button type="button" @click="removeItem(index)" class="btn-danger">Remove</button></td>
            </tr>
          </tbody>
        </table>
        <div class="invoice-total">
          <strong>Grand Total: ₦{{ formatPrice(grandTotal) }}</strong>
        </div>
      </div>

      <!-- Submission -->
      <div class="form-actions">
        <button type="submit" :disabled="isSubmitting" class="btn-primary">
          {{ isSubmitting ? 'Saving...' : 'Save Invoice' }}
        </button>
        <div v-if="error" class="error">{{ error }}</div>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import apiClient from '../api';

const router = useRouter();
const toast = useToast();

// --- Reactive State ---
const customers = ref([]);
const books = ref([]);
const invoice = ref({
  customer_id: '',
  due_date: new Date().toISOString().slice(0, 10), // Default to today
  status: 'UNPAID',
  items: [],
});
const newItem = ref({
  book_id: '',
  quantity: 1,
});

const isSubmitting = ref(false);
const error = ref(null);

// --- API Calls & Data Loading ---
onMounted(async () => {
  try {
    const [customerRes, bookRes] = await Promise.all([
      apiClient.get('/customers/'),
      apiClient.get('/books/'),
    ]);
    customers.value = customerRes.data;
    books.value = bookRes.data;
  } catch (err) {
    error.value = 'Failed to load initial customer and book data.';
    toast.error(error.value);
  }
});

const submitInvoice = async () => {
  if (invoice.value.items.length === 0) {
    toast.warning('Please add at least one item to the invoice.');
    return;
  }
  if (!invoice.value.customer_id) {
    toast.warning('Please select a customer.');
    return;
  }
  isSubmitting.value = true;
  error.value = null;
  try {
    await apiClient.post('/invoices/', invoice.value);
    toast.success("Invoice created successfully!");
    router.push('/invoices');
  } catch (err) {
    error.value = 'Failed to create invoice. Please check the data and try again.';
    toast.error(error.value);
    console.error(err);
  } finally {
    isSubmitting.value = false;
  }
};

// --- Helper Functions ---
const getBookDetails = (bookId) => {
  return books.value.find(b => b.id === bookId) || { title: 'N/A', price: 0 };
};

const addItem = () => {
  if (!newItem.value.book_id || newItem.value.quantity <= 0) {
    toast.warning('Please select a book and enter a valid quantity.');
    return;
  }
  invoice.value.items.push({ ...newItem.value });
  // Reset form
  newItem.value.book_id = '';
  newItem.value.quantity = 1;
};

const removeItem = (index) => {
  invoice.value.items.splice(index, 1);
};

const grandTotal = computed(() => {
  return invoice.value.items.reduce((total, item) => {
    const book = getBookDetails(item.book_id);
    return total + (item.quantity * (book.price || 0));
  }, 0);
});

const formatPrice = (value) => {
    const num = parseFloat(value);
    if (isNaN(num)) return '0.00';
    return num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}
</script>

<style scoped>
.create-invoice { 
  max-width: 900px; 
  margin: auto; 
  padding: 20px;
}
.invoice-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.form-section { 
  background: #f9f9f9; 
  border: 1px solid #eee; 
  padding: 20px; 
  border-radius: 8px; 
}
.form-section h3 {
  margin-top: 0;
  border-bottom: 1px solid #ddd;
  padding-bottom: 10px;
  margin-bottom: 20px;
}
select, input {
  width: 100%;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}
.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.add-item-form { 
  display: flex; 
  gap: 10px; 
  align-items: center; 
}
.add-item-form select {
  flex-grow: 1;
}
.qty-input {
  width: 80px;
}
.items-table { 
  margin-top: 20px; 
}
table { 
  width: 100%; 
  border-collapse: collapse; 
}
th, td { 
  border: 1px solid #ddd; 
  padding: 12px;
  text-align: left;
}
th {
  background-color: #f2f2f2;
}
.invoice-total { 
  text-align: right; 
  font-size: 1.4rem; 
  margin-top: 20px; 
  font-weight: bold;
}
.form-actions { 
  margin-top: 20px; 
}
.btn-primary { 
  background-color: #42b983; 
  color: white; 
  padding: 12px 20px; 
  border: none; 
  border-radius: 5px; 
  cursor: pointer; 
  font-size: 1rem;
}
.btn-primary:disabled { 
  background-color: #aaa; 
  cursor: not-allowed;
}
.btn-secondary {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
}
.btn-danger { 
  background-color: #d0021b; 
  color: white; 
  border: none; 
  padding: 5px 10px; 
  cursor: pointer; 
  border-radius: 4px; 
}
.error { 
  color: red; 
  margin-top: 10px; 
  font-weight: bold;
}
</style>