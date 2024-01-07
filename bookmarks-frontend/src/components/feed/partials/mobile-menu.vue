<template>
    <nav class="nav-menu">
    <button
        class="btn relative" 
        type="button"
        @click="isShowingMenu = !isShowingMenu"
    >
        <IconMenu />
    </button>

    <div id="nav_menu_sidebar" 
        v-if="isShowingMenu" 
        class="d_hidden nav-menu-sidebar" 
        ref="mobileMenu"
    >
        <h3 class="n-m-s--header">Biblio</h3>
        <div class="n-m-s--content">
            <button 
                class="n-m-s--li"
                alt="settings"
                @click="router.push(pathToSettings)"
            >
                Settings
                <IconSettings />
            </button>
        </div>
    </div>
</nav> 
</template>
<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import IconSettings from '../../svg/icon-settings.vue';
import IconMenu from '../../svg/icon-hmenu.vue';
import { autoCloseElementWithRef } from  './autoclose';
const router = useRouter();
const route = useRoute();
const { user } = route.params;
const pathToSettings = `/feed/${user}/settings`

const isShowingMenu = ref(false);
const mobileMenu = ref(null);
// Handle all event listeners for clicking in and out of menu to auto close it.

onMounted(() => {
    
});

onUnmounted(() => {

})

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
}

.btn {
    background-color: var(--gray-50);
    padding: var(--btn-padding-sm);
    border-radius: var(--radius-sm);
    transition: all 150ms ease;
    height: 40px;
}

.btn:hover {
    background-color: var(--gray-200);
    transform: scale(1.05);
}

.nav-menu-sidebar {
    position: absolute;
    top: 65px;
    right: 20px;
    width: 80vw;
    max-width: 480px;
    transition: var(--transition-short);
    border-radius: var(--radius-sm);
    box-shadow: var(--shadow-lg);
    overflow-y: clip;
}

.n-m-s--header {
    background-color: var(--surface-primary);
    padding: var(--padding-sm);
    padding-left: calc(var(--padding-sm) + var(--margin-shim-sm));
    font-size: var(--font-xl);
    font-weight: 600;
    color: var(--stone-600);
}

.n-m-s--content {
    background-color: var(--gray-100);
}

.n-m-s--li {
    display: flex;
    padding: var(--padding-sm);
    padding-left: calc(var(--padding-sm) + var(--margin-shim-sm));
    align-items: center;
    justify-content: space-between;
    width: 100%;
}

.n-m-s--li:hover {
    background-color: var(--stone-300);
    color: var(--stone-800);
}
</style>