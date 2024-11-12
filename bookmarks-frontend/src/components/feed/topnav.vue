<template>
  <nav class="nav-menu">
    <div class="flex space-between w-100 items-bottom">
      <h4 class="text-stone-600 fancy pl-2">HardcoverLit</h4>

      <div class="flex gap-2 items-bottom">
          <NavSearchBar/>

          <Notifications />
          
          <MobileMenu />
      </div>
    </div>
  </nav>
</template>
<script setup>
  import Notifications from './social/Notifications.vue';
  import MobileMenu from './partials/mobile-menu.vue';
  import NavSearchBar from './navigation/NavSearchBar.vue';

</script>
<style scoped>
.nav-menu {
    position: sticky;
    height: 40px;
    margin-bottom: 10px;
    top: 0;
    right: 0;
    width: 100%;
    display: flex;
    justify-content: end;
    padding: var(--padding-md);
    padding-top: var(--padding-sm);
    z-index: 1000;
    background: linear-gradient(90deg, var(--surface-primary), transparent)
}
</style> 