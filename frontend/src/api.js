import axios from 'axios';

// Function to get the CSRF token from the browser cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
  headers: {
    'Content-Type': 'application/json'
  }
});

// THIS IS THE MAGIC PART:
// Add an interceptor that attaches the CSRF token to every state-changing request
apiClient.interceptors.request.use((config) => {
  const methods = ['post', 'put', 'patch', 'delete'];
  if (methods.includes(config.method.toLowerCase())) {
    config.headers['X-CSRFToken'] = getCookie('csrftoken');
  }
  return config;
});

export default apiClient;