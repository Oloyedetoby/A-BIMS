<template>
  <PaymentModal :show="show" @close="$emit('cancel')">
    <div class="confirm-dialog">
      <h3>{{ title }}</h3>
      <p>{{ message }}</p>
      <div class="dialog-actions">
        <button @click="$emit('cancel')" class="btn-secondary">Cancel</button>
        <button @click="$emit('confirm')" class="btn-danger">Confirm Delete</button>
      </div>
    </div>
  </PaymentModal>
</template>

<script setup>
import PaymentModal from './PaymentModal.vue';

defineProps({
  show: Boolean,
  title: { type: String, default: 'Confirm Action' },
  message: { type: String, default: 'Are you sure you want to proceed? This action cannot be undone.' }
});
defineEmits(['cancel', 'confirm']);
</script>

<style scoped>
.confirm-dialog { text-align: center; }
.confirm-dialog h3 { margin-top: 0; }
.dialog-actions { 
  margin-top: 25px; 
  display: flex; 
  gap: 15px; 
  justify-content: center; 
}
.btn-secondary, .btn-danger {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}
.btn-secondary { background-color: #6c757d; color: white; }
.btn-danger { background-color: #d0021b; color: white; }
</style>