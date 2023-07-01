<template>
    <footer>
        <div class="vertical-button-group">
            <button class="footer-nav-button" alt="feed">
                <IconBook/>
            </button>
            <p>Feed</p>
        </div>

        <div class="vertical-button-group">
            <button class="footer-nav-button" alt="feed">
                <IconSocial/>
            </button>
            <p>Social</p>
        </div>

        <div class="vertical-button-group">
            <button class="footer-nav-button" alt="feed">
                <IconExplore/>
            </button>
            <p>Explore</p>
        </div>
    </footer>
</template>


<script setup>
import IconBook from '@/components/svg/icon-book.vue'
import IconSocial from '@/components/svg/icon-social.vue';
import IconExplore from '@/components/svg/icon-explore.vue';

</script>

<style scoped>
footer {
    position: fixed;   
    bottom: 0;
    left: 0;
    width: 100%;
    display: flex;
    justify-content: space-around;
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
    border: solid 2px #343fa9;
    color: #343fa9;
    transform: scale(1.02);
}

.vertical-button-group {
    display: grid;
    grid-template-columns: 1;
    justify-items: center;
    align-items: center;
    gap: .25rem;
    cursor: pointer;
    color: #5A67D8;
    font-weight: 500;
}
</style>