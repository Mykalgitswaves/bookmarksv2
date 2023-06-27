<template>
    <footer>
        <button class="footer-nav-button">
            <IconBook/>
        </button>
    </footer>
</template>


<script setup>
import IconBook from '@/components/svg/icon-book.vue'

</script>

<style scoped>
footer {
 position: fixed;   
 bottom: 0;
 left: 0;
 width: 100%;
 display: flex;
 justify-content: space-between;
 padding: 1.25rem;
 background: rgba(243, 244, 246, 98%);
}

.footer-nav-button {
    border-radius: 50%;
    padding: .5rem;
    margin-left: 1rem;
    margin-right: 1rem;
    color: #667EEA;
    border: solid 2px #667EEA;
    align-content: center;
    justify-content: center;
    transition-duration: 250ms;
}
.footer-nav-button:hover {
    border: solid 2px #5A67D8;
    color: #5A67D8;
    transform: scale(1.02);
}
</style>