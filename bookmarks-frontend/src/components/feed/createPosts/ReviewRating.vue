<template>
<div class="m-tb-40">
    <h1 class="heading light">What did you think of the book?</h1>

    <form class="rating-radio-group">
        <label class="rating-label" for="rating-3">
            <IconHappy class="rating-svg" :class="{'active': modelValue === 3}" />

            <h2 class="rating-label-text">I loved it</h2>
            <!-- These inputs are visually hidden -->

            <input v-model="modelValue" 
                id="rating-3" 
                name="rating"
                type="radio"
                class="rating-checkbox"
                :value="3"
            >
        </label>
        
        <label class="rating-label" for="rating-2">
            <IconAmbivalent class="rating-svg" :class="{'active': modelValue === 2}" />

            <h2 class="rating-label-text">I liked it</h2>

            <input v-model="modelValue" 
                id="rating-2"
                name="rating"
                type="radio"
                class="rating-checkbox"
                :value="2"
            >
        </label>

        <label class="rating-label" for="rating-1">
            <IconDisliked class="rating-svg" :class="{'active': modelValue === 1}" />
            <h2 class="rating-label-text">It wasn't for me</h2>

            <input v-model="modelValue" 
                id="rating-1"
                name="rating"
                type="radio"
                class="rating-checkbox"
                :value="1"
            >
        </label>
    </form>
</div>
</template>
<script setup>
import { ref, watch } from 'vue';
import IconHappy from '../../svg/icon-happy.vue';
import IconAmbivalent from '../../svg/icon-ambivalent.vue';
import IconDisliked from '../../svg/icon-disliked.vue';

const emits = defineEmits(['set-rating']);

const modelValue = ref(null);

watch(modelValue, (newValue) => {
    emits('set-rating', newValue);
});
</script>
<style scoped>
.rating-radio-group {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    column-gap: 20px;
    row-gap: 20px;
    margin-top: 40px;
    justify-items: center;
}

.rating-label  {
    padding: var(--padding-sm);
    background-color: transparent;
    border-radius: var(--radius-md);
    display: grid;
    place-content: center;
    text-align: center;
    border: 1px solid var(--indigo-400);
}

.rating-label:has(input:checked) {
    background-color: var(--indigo-200);
    transform: scale(1.02) ;
}

.rating-label:has(input:checked) .rating-label-text {
    color: var(--indigo-500)
}

.rating-label-text {
    font-size: var(--font-lg);
    font-family: var(--fancy-script);
    margin-top: var(--margin-sm);
    color: var(--indigo-400);
}

.rating-label input {
    appearance: none;
}

.rating-svg {
    width: 48px;
    fill: var(--indigo-400);
    transition: all 100ms linear;
    margin-left: auto;
    margin-right: auto;
}

.rating-svg.active {
    fill: var(--indigo-500);
}
</style>