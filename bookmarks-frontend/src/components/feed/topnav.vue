<template>
  <MobileMenu/>
</template>

<script setup>
  import MobileMenu from './partials/mobile-menu.vue';

</script>

<style scoped>
.navbar-p {
  padding: 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center; 
}

.profile-image {
  height: 3rem;
  border-radius: 50%;
  opacity: 1;
}

.tab-group {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(2, minmax(160px, 200px));
    justify-content: center;
}

.tab-btn {
    color: #718096;
    border-bottom: solid .25rem #dbdada;
    padding-bottom: .5rem;
}

.active {
    border-bottom: solid .25rem #5A67D8;
    color: #5A67D8;
}

.reverse {
    flex-direction: row-reverse;
}

@media only screen and (max-width: 768px)  {
  .navbar-text {
      display: none;
  }
}

.top-menu-wrapper {
  position: absolute;
  top: 15vh;
  right: 0;
  z-index: 10;
  padding: 2rem;
  width: minmax(60vw, 280px);
  border-bottom-left-radius: 4px;
}

</style>