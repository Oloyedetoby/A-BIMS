import { createRouter, createWebHistory } from 'vue-router';

// --- Layouts ---
import App from '../App.vue'; 
import BlankLayout from '../layouts/BlankLayout.vue';

// --- Page Views (Checked for correctness) ---
import DashboardView from '../views/DashboardView.vue';
import CustomersView from '../views/CustomersView.vue';
import CustomerDetailView from '../views/CustomerDetailView.vue';
import BooksView from '../views/BooksView.vue';
import BookDetailView from '../views/BookDetailView.vue';
import InvoicesView from '../views/InvoicesView.vue';
import CreateInvoiceView from '../views/CreateInvoiceView.vue';

// --- Management Page Views (Checked for correctness) ---
import AuthorsView from '../views/AuthorsView.vue';
import AuthorDetailView from '../views/AuthorDetailView.vue';
import PublishersView from '../views/PublishersView.vue';
import PublisherDetailView from '../views/PublisherDetailView.vue';
import RouteAxesView from '../views/RouteAxesView.vue';
import RouteAxisDetailView from '../views/RouteAxisDetailView.vue'; // The import is here and correct
import InsightsView from '../views/InsightsView.vue';
// --- Special Views (Checked for correctness) ---
import PrintReceiptView from '../views/PrintReceiptView.vue';


const routes = [
  // Routes that use the main layout with the navbar
  {
    path: '/',
    component: App,
    children: [
      { path: '', name: 'Dashboard', component: DashboardView },
      
      { path: 'customers', name: 'Customers', component: CustomersView },
      { path: 'customers/:id', name: 'CustomerDetail', component: CustomerDetailView },
      
      { path: 'books', name: 'Books', component: BooksView },
      { path: 'books/:id', name: 'BookDetail', component: BookDetailView },
      
      { path: 'invoices', name: 'Invoices', component: InvoicesView },
      { path: 'invoices/new', name: 'CreateInvoice', component: CreateInvoiceView },
      
      { path: 'authors', name: 'Authors', component: AuthorsView },
      { path: 'authors/:id', name: 'AuthorDetail', component: AuthorDetailView },

      { path: 'publishers', name: 'Publishers', component: PublishersView },
      { path: 'publishers/:id', name: 'PublisherDetail', component: PublisherDetailView },
      { path: '/insights', name: 'Insights', component: InsightsView },
      
      { path: 'route-axes', name: 'RouteAxes', component: RouteAxesView },
      { path: 'route-axes/:id', name: 'RouteAxisDetail', component: RouteAxisDetailView }, // The route is here and correct
    ]
  },
  
  // Routes that use the blank layout (for printing, etc.)
  {
    path: '/print',
    component: BlankLayout,
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