<template>
  <GenericManagement 
    title="Manage Authors"
    apiEndpoint="authors"
    itemName="Authors"
    detailRouteName="AuthorDetail"
  />
</template>

<script setup>
import GenericManagement from '../components/GenericManagement.vue';
</script>