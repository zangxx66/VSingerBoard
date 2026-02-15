<script setup lang="ts">
  defineProps({
    title: {
      type: String,
      required: true,
    },
  })
  defineOptions({
    name: 'LineHeader',
  })
</script>
<template>
  <div class="line-header">
    <div class="line-header-title">
      <slot name="prefix"></slot>
      {{ title }}
      <slot name="suffix"></slot>
    </div>
  </div>
</template>
