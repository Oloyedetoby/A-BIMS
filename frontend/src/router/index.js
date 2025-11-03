import { createRouter, createWebHistory } from 'vue-router';

// Import layouts
import App from '../App.vue'; 
import BlankLayout from '../layouts/BlankLayout.vue';

// THIS IS THE CORRECTED & COMPLETE LIST OF VIEW IMPORTS
import DashboardView from '../views/DashboardView.vue';
import CustomersView from '../views/CustomersView.vue';
import CustomerDetailView from '../views/CustomerDetailView.vue'; // Was missing
import BooksView from '../views/BooksView.vue';
import BookDetailView from '../views/BookDetailView.vue';       // Was missing
import AuthorsView from '../views/AuthorsView.vue';           // Was missing
import PublishersView from '../views/PublishersView.vue';     // Was missing
import RouteAxesView from '../views/RouteAxesView.vue';       // Was missing
import InvoicesView from '../views/InvoicesView.vue';
import CreateInvoiceView from '../views/CreateInvoiceView.vue'; // Was missing
import PrintReceiptView from '../views/PrintReceiptView.vue';


const routes = [
  {
    path: '/',
    component: App, // Use the main layout with the navbar
    children: [
      { path: '', name: 'Dashboard', component: DashboardView },
      { path: '/customers', name: 'Customers', component: CustomersView },
      { path: '/customers/:id', name: 'CustomerDetail', component: CustomerDetailView },
      { path: '/books', name: 'Books', component: BooksView },
      { path: '/books/:id', name: 'BookDetail', component: BookDetailView },
      { path: '/authors', name: 'Authors', component: AuthorsView },
      { path: '/publishers', name: 'Publishers', component: PublishersView },
      { path: '/route-axes', name: 'RouteAxes', component: RouteAxesView },
      { path: '/invoices', name: 'Invoices', component: InvoicesView },
      { path: '/invoices/new', name: 'CreateInvoice', component: CreateInvoiceView },
    ]
  },
  {
    path: '/print',
    component: BlankLayout, // Use the blank layout for all print routes
    children: [
      {
        path: 'invoice/:invoiceId/payment/:paymentId',
        name: 'PrintReceipt',
        component: PrintReceiptView,
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;