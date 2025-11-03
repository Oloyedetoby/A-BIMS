<template>
  <PaymentModal :show="show" @close="$emit('close')">
    <form @submit.prevent="submitForm">
      <h3>Create Credit Note / Book Return</h3>

      <div v-if="fullInvoice && !isSubmitting">
        <div class="form-group">
          <label>Original Invoice:</label>
          <p><strong>#{{ fullInvoice.id }} ({{ fullInvoice.invoice_date }})</strong> for <strong>{{ fullInvoice.customer_name }}</strong></p>
        </div>
        
        <div class="form-group">
          <label for="reason">Reason for Return:</label>
          <input type="text" id="reason" v-model="creditNote.reason" placeholder="e.g., Unsold book returns">
        </div>
        
        <h4>Items to Return:</h4>
        <div v-if="creditNote.items.length > 0" class="items-list">
            <div v-for="item in creditNote.items" :key="item.id" class="return-item">
              <span class="item-name">{{ item.book_name }} <small>(Sold at ₦{{ item.unit_price }})</small></span>
              <div class="quantity-control">
                  <label :for="`item-${item.id}`">Qty to Return:</label>
                  <input :id="`item-${item.id}`" type="number" v-model.number="item.return_quantity" min="0" :max="item.original_quantity">
                  <span class="max-qty">/ {{ item.original_quantity }} available</span>
              </div>
            </div>
        </div>
        <p v-else>No items found on this invoice.</p>

        <div class="form-actions">
          <button type="button" @click="$emit('close')" class="btn-secondary">Cancel</button>
          <button type="submit" class="btn-primary" :disabled="isSubmitting">
            {{ isSubmitting ? 'Saving...' : 'Save Credit Note' }}
          </button>
        </div>
        <div v-if="error" class="error">{{ error }}</div>
      </div>
      <div v-else>
          <p>Loading invoice details...</p>
      </div>
    </form>
  </PaymentModal>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useToast } from 'vue-toastification';
import apiClient from '../api';
import PaymentModal from './PaymentModal.vue';

const props = defineProps({
  show: Boolean,
  invoice: Object, // The original invoice object (with the customer object attached)
});
const emit = defineEmits(['close', 'credit-note-saved']);
const toast = useToast();

const fullInvoice = ref(null);
const creditNote = ref({ items: [] });
const isSubmitting = ref(false);
const error = ref(null);

watch(() => props.show, async (newShowState) => {
  if (newShowState && props.invoice) {
    // Modal is opening, let's fetch the full invoice data
    isSubmitting.value = true;
    error.value = null;
    fullInvoice.value = null;
    try {
      const response = await apiClient.get(`/invoices/${props.invoice.id}/`);
      fullInvoice.value = response.data;

      creditNote.value = {
        reason: 'Unsold book returns',
        items: fullInvoice.value.items.map(item => ({
          id: item.id,
          book_id: item.book_id,
          book_name: item.book,
          unit_price: item.unit_price,
          original_quantity: item.quantity,
          return_quantity: 0,
        })),
      };
    } catch (err) {
      error.value = "Failed to load invoice items for credit note.";
      toast.error(error.value);
    } finally {
      isSubmitting.value = false;
    }
  }
});

const submitForm = async () => {
  isSubmitting.value = true;
  error.value = null;

  const itemsToReturn = creditNote.value.items
    .filter(item => item.return_quantity > 0 && item.return_quantity <= item.original_quantity)
    .map(item => ({
      book_id: item.book_id,
      quantity: item.return_quantity,
      unit_price: item.unit_price,
    }));

  if (itemsToReturn.length === 0) {
    toast.warning("Please enter a quantity for at least one item to return.");
    isSubmitting.value = false;
    return;
  }
  
  // THIS IS THE CORRECTED PART:
  // We get the customer.id from the invoice prop passed by the parent component,
  // which we ensured has the full customer object attached to it.
  const payload = {
    customer: props.invoice.customer.id, 
    original_invoice: props.invoice.id,
    reason: creditNote.value.reason,
    items: itemsToReturn,
  };

  try {
    await apiClient.post('/credit-notes/', payload);
    toast.success("Credit note created successfully!");
    emit('credit-note-saved');
  } catch (err) {
    error.value = 'Failed to create credit note.';
    toast.error(error.value);
    console.error("Credit Note Error:", err.response?.data);
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
h3 { margin-top: 0; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 20px;}
.form-group { margin-bottom: 20px; }
.form-group label { display: block; font-weight: bold; margin-bottom: 5px; }
.form-group p { margin: 0; }
.form-group input { width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #ccc; }
.items-list { margin-top: 20px; }
.return-item { 
    display: flex; 
    align-items: center; 
    justify-content: space-between;
    gap: 15px; 
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid #f0f0f0;
}
.item-name { flex-grow: 1; font-weight: 500; }
.item-name small { color: #555; display: block; font-weight: normal; }
.quantity-control { display: flex; align-items: center; gap: 8px; }
.quantity-control input { width: 70px; text-align: right; padding: 8px; }
.max-qty { color: #666; font-size: 0.9em; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 30px; }
.btn-primary, .btn-secondary { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
.btn-primary { background-color: #42b983; color: white; }
.btn-secondary { background-color: #6c757d; color: white; }
.error { color: red; margin-top: 10px; text-align: right; }
</style>