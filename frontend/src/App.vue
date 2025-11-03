<template>
  <div id="app-wrapper">
    <header>
      <h1>Amen Books Management System</h1>
      <!-- This is the CORRECTED version -->
      <nav>
        <router-link to="/">Dashboard</router-link>
        <router-link to="/customers">Customers</router-link>
        <router-link to="/books">Books</router-link>
        <router-link to="/authors">Authors</router-link>
        <router-link to="/invoices">Invoices</router-link>
        <router-link to="/publishers">Publishers</router-link>
        <router-link to="/route-axes">Route/Axes</router-link>
      </nav>
    </header>
    <main>
      <!-- The current page component will be rendered here by Vue Router -->
      <router-view />
    </main>
  </div>
</template>

<script setup>
// No script needed for this component anymore
</script>

<style>
/* Global styles for the entire application */
body {
  margin: 0;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

#app-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

header {
  background-color: #2c3e50;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

header h1 {
  margin: 0;
  font-size: 1.5rem;
}

nav {
  display: flex;
  gap: 1.5rem;
}

nav a {
  color: white;
  text-decoration: none;
  font-weight: bold;
  padding: 0.5rem;
  border-radius: 4px;
}

/* Style for the currently active link */
nav a.router-link-exact-active {
  background-color: #42b983;
}

main {
  padding: 2rem;
}
</style>