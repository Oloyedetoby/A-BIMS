import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// --- START: Add these lines for notifications ---
import Toast from 'vue-toastification'
// Import the CSS or use your own!
import 'vue-toastification/dist/index.css'
// --- END: Add these lines ---


const app = createApp({
  template: '<router-view />'
})

app.use(router)
app.use(Toast) // <-- TELL VUE TO USE THE TOAST PLUGIN

app.mount('#app')