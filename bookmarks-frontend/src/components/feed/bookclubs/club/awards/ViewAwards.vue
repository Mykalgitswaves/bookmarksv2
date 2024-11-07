<template>
<button 
    ref="awardsButton"
    class="btn btn-ghost btn-tiny text-sm btn-icon"
    @click="showOrHideAwardsDialog()"    
>
    Awards
</button>

<dialog ref="awardsModal" class="awards-meny">
    <div class="pt-5 pb-5 flex items-center">
            <h4 class="text-stone-500 text-lg italic">Awards</h4>

            <CloseButton class="ml-auto" @close="awardsModal.close()"/>
    </div>
    <div>
        hullo
    </div>
</dialog>
</template>
<script setup>

import { ref, watch } from 'vue';

const awardsButton = ref(null);
const awardsModal = ref(null);
const isOpen = ref(false);

/**
 * @UI_functions
 */
function showOrHideAwardsDialog() {
    if (awardsModal.value) {
        if (!awardsModal.value.open) { 
            awardsModal.value.showModal(); 
            isOpen.value = true; 
        } else {
            awardsModal.value.close();
            isOpen.value = false;
        } 
    }
}


function handleClickOutside(event){
    if (
        awardsModal.value 
        && awardsModal.value.open 
        && !(awardsModal.value.contains(event.target) || 
        awardsButton.value.contains(event.target))
    ) {
        awardsModal.value.close();
        isOpen.value = false;
    }
}

// Make a watcher for an event listener when someone clicks outside the dialog. 
watch(
    isOpen, 
    (newValue) => {
        if (newValue) {
            document.addEventListener('click', (event) => handleClickOutside(event));
            watch();
        }
    },
);
</script>
<style scoped>
.h-40 {
    height: 40px;
}

.transition {
    transition: all 250ms ease-in-out;
}

@starting-style {
    .awards-menu {
        opacity: 0;
        height: 0;
        right: -9999px;
    }
}

.awards-menu[open] {
    --mobile-sidebar-width: 70vw;
    @media screen and (min-width: 768px) {
        --mobile-sidebar-width: 700px;
    }

    transition-behavior: allow-discrete;
    transition: 300ms ease;
    width: var(--mobile-sidebar-width);
    min-width: 300px; /** For mobile */
    border: 1px solid var(--stone-200);
    border-radius: var(--radius-md);
    margin: var(--margin-md);
    margin-left: auto;
    margin-top: 60px;
    padding: 24px;
    padding-top: 0;
    background-color: var(--stone-50);
}

.awards-menu::backdrop {
  display:none
}
</style>