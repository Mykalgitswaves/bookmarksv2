<template>
    <BackBtn/>
    <section>
        <div class="mt-10">
            <h1 class="title">Your bookshelves</h1>
            
            <div class="bookshelves">
                
            </div>
        </div>
       <RouterView></RouterView>
    </section>
</template>
<script setup>
import BackBtn from './partials/back-btn.vue';

const bookshelves = [{name: 'new', id: 'new', }]

</script>
<style scoped>
.bookshelves {

}

.title {
    font-size: var(--font-3xl);
    font-weight: medium;
    color: var(--slate-600);
}
</style>

