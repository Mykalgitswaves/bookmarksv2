<template>
  <nav class="nav-menu">
    <div class="flex w-100 items-bottom justify-between">
      <h4 v-if="!isSearchFocused" class="transition text-stone-600 fancy pl-2 pt-2">HardcoverLit</h4>

      <div class="flex gap-2 items-bottom ml-auto justify-end"  style="min-width: 200px">
          <NavSearchBar @is-search-focused="(value) => isSearchFocused = value"/>

          <Notifications />
      </div>
    </div>
  </nav>
</template>
<script setup>
  import Notifications from './social/Notifications.vue';
  import MobileMenu from './partials/mobile-menu.vue';
  import NavSearchBar from './navigation/NavSearchBar.vue';
  import { ref } from 'vue';

  const isSearchFocused = ref(false);
</script>
<style scoped>
@starting-style {
  .transition {
    opacity: 0;
    width: 40px;
  }
}

.transition {
  transition: all 250ms ease-in-out;
}

.nav-menu {
    position: sticky;
    height: 40px;
    margin-bottom: 10px;
    top: 0;
    right: 0;
    width: 100%;
    display: flex;
    justify-content: end;
    /* align-items: end; */
    padding: var(--padding-md);
    padding-top: var(--padding-sm);
    z-index: 1000;
    background-color: var(--surface-primary);
    padding-bottom: 50px;
    border-bottom: 1px solid var(--indigo-200);
}
</style> 