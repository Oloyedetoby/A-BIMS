<template>
  <div class="receipt-wrapper">
    <div class="receipt-content">
      <header>
        <h2>Payment Receipt</h2>
        <h1>Amen Books & Marketing</h1>
        <p>123 Business Rd, Lagos, Nigeria</p>
      </header>
      
      <section class="details">
        <div><strong>Receipt No:</strong> PMT-{{ payment?.id }}</div>
        <div><strong>Date:</strong> {{ payment?.payment_date }}</div>
      </section>

      <section class="customer-info">
        <h4>BILLED TO:</h4>
        <p><strong>{{ invoice?.customer_name }}</strong></p>
      </section>

      <section class="payment-details">
        <table>
          <thead>
            <tr>
              <th>Description (Items from Invoice #{{ invoice?.id }})</th>
              <th class="text-right">Price</th>
            </tr>
          </thead>
          <!-- NEW: List the actual items from the invoice -->
          <tbody>
            <tr v-for="item in invoice?.items" :key="item.id">
              <td>{{ item.quantity }} x {{ item.book }}</td>
              <td class="text-right">₦{{ formatPrice(item.quantity * item.unit_price) }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="spacer"><td colspan="2"></td></tr>
            <tr>
              <td class="text-right"><strong>Total Amount:</strong></td>
              <td class="text-right">₦{{ formatPrice(invoice?.total_amount) }}</td>
            </tr>
            <tr>
              <td class="text-right"><strong>Amount Paid (This Txn):</strong></td>
              <td class="text-right"><strong>₦{{ formatPrice(payment?.amount) }}</strong></td>
            </tr>
             <tr class="spacer"><td colspan="2"></td></tr>
            <tr>
              <td class="text-right"><strong>Balance Due:</strong></td>
              <td class="text-right balance"><strong>₦{{ formatPrice(invoice?.balance_due) }}</strong></td>
            </tr>
          </tfoot>
        </table>
      </section>

      <section class="footer">
        <p>Thank you for your business!</p>
      </section>
    </div>
  </div>
</template>

<script setup>
defineProps({
  payment: Object,
  invoice: Object
});

const formatPrice = (value) => {
  const num = parseFloat(value);
  return isNaN(num) ? '0.00' : num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
};
</script>

<style scoped>
/* BOLDER, CLEANER STYLES */
.receipt-wrapper {
  font-family: 'Consolas', 'Menlo', monospace;
  width: 80mm;
  margin: 10px auto;
  color: #000;
  font-size: 12px; /* Base font size */
}
header { text-align: center; border-bottom: 2px dashed #000; margin-bottom: 10px; padding-bottom: 10px; }
header h1 { margin: 5px 0; font-size: 1.4em; font-weight: bold; }
header h2 { margin: 0; font-size: 1.1em; }
header p { margin: 0; }
.details, .customer-info { margin-bottom: 15px; }
h4 { margin: 10px 0 5px; font-size: 1em; border-bottom: 1px solid #000; }
.customer-info p { margin: 0; font-size: 1.1em; }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; border-bottom: 1px solid #000; padding-bottom: 5px; }
td { padding: 4px 0; }
tfoot { border-top: 1px solid #000; font-size: 1.1em; }
tfoot .spacer td { padding: 5px 0; }
.text-right { text-align: right; }
.balance { font-size: 1.2em; }
.footer { text-align: center; border-top: 2px dashed #000; margin-top: 10px; padding-top: 10px; }
</style>