import { createRouter, createWebHistory } from 'vue-router';
import DashboardView from '../views/DashboardView.vue';
import CustomersView from '../views/CustomersView.vue';
import BooksView from '../views/BooksView.vue';
import InvoicesView from '../views/InvoicesView.vue';
import CreateInvoiceView from '../views/CreateInvoiceView.vue';

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: DashboardView,
  },
  {
    path: '/customers',
    name: 'Customers',
    component: CustomersView,
  },
  {
    path: '/books',
    name: 'Books',
    component: BooksView,
  },
  {
    path: '/invoices',
    name: 'Invoices',
    component: InvoicesView,
  },
  {
  path: '/invoices/new',
  name: 'CreateInvoice',
  component: CreateInvoiceView,
},
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;