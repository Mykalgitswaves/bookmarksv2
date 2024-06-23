<template>
    <nav class="nav-menu">
        <div class="flex space-between w-100 items-bottom">
            <!-- We need to get our marketing site up and running tbd -->
            <!-- href="https://www.hardcoverlit.com/home" -->
            <!-- Switch this to an a tag finally -->
            <h4 class="text-stone-600 fancy pl-2">HardcoverLit</h4>
            
            <button
            ref="mobileMenuButton"
            class="btn relative" 
            type="button"
            :class="{'active': isMobileMenuShowing}"
            @click="isMobileMenuShowing = !isMobileMenuShowing"
            >
                <IconMenu />
            </button>
        </div>

    <Transition name="content">
        <div id="nav_menu_sidebar" 
            v-show="isMobileMenuShowing" 
            class="d_hidden nav-menu-sidebar" 
            ref="mobileMenu"
        >
            <h3 class="n-m-s--header fancy">HardcoverLit</h3>

            <div class="n-m-s--content">
                <button 
                    class="n-m-s--li fancy"
                    alt="settings"
                    @click="router.push(pathToSettings)"
                >
                    Settings
                </button>
            </div>

            <div class="n-m-s--content">
                <button 
                    class="n-m-s--li fancy"
                    alt="settings"
                    @click="logOut"
                >
                    Log out
                </button>
            </div>
        </div>
    </Transition>
</nav> 
</template>
<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import IconMenu from '../../svg/icon-hmenu.vue';
import { autoCloseElementWithRef, isMobileMenuShowing} from  './autoclose';
const router = useRouter();
const route = useRoute();
const { user } = route.params;
const pathToSettings = `/feed/${user}/settings`

const mobileMenu = ref(null);
const mobileMenuButton = ref(null);

// Handle all event listeners for clicking in and out of menu to auto close it.
onMounted(() => {
    autoCloseElementWithRef([mobileMenu.value, mobileMenuButton.value]);
});

function logOut() {
    document.cookie = 'token'+'=; Max-Age=-99999999;';
    router.push('/');
}
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

.btn {
    background-color: var(--gray-50);
    padding: var(--btn-padding-sm);
    border-radius: var(--radius-sm);
    transition: all 150ms ease;
    height: 40px;
}

.btn.active {
    background-color: var(--indigo-100);
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
    overflow: clip;
}

.n-m-s--header {
    background-color: var(--surface-primary);
    padding: var(--padding-sm);
    padding-left: calc(var(--padding-sm) + var(--margin-shim-sm));
    font-size: var(--font-xl);
    font-weight: 400;
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
    background-color: var(--indigo-100);
    color: var(--stone-800);
}
</style>