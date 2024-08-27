<template>
    <div class="m-tb-40">
        <h1 class="text-2xl fancy text-stone-700">What pace is your club</h1>

        <form class="rating-radio-group">
            <label class="rating-label" for="rating-1">
                <IconSteady 
                    class="rating-svg text-indigo-500" 
                    :class="{'active': modelValue === 1}" 
                />

                <h2 class="rating-label-text">Casual</h2>

                <input v-model="modelValue" 
                    id="rating-1"
                    name="rating"
                    type="radio"
                    class="rating-checkbox"
                    :value="1"
                >
                <span class="text-sm text-stone-700">About 1 book every 3 months</span> 
            </label>

            <label class="rating-label" for="rating-2">
                
                <IconCasual 
                    class="rating-svg text-indigo-500" 
                    :class="{'active': modelValue === 2}" 
                />

                <h2 class="rating-label-text">Steady</h2>
                <!-- These inputs are visually hidden -->

                <input v-model="modelValue" 
                    id="rating-2" 
                    name="rating"
                    type="radio"
                    class="rating-checkbox"
                    :value="2"
                >
                <span class="text-sm text-stone-700">About 1 book every month</span> 
            </label>

            <label class="rating-label" for="rating-3">
                <IconBlazing class="rating-svg text-indigo-500" :class="{'active': modelValue === 3}"/>
                <h2 class="rating-label-text">Blazing</h2>

                <input v-model="modelValue" 
                    id="rating-3"
                    name="rating"
                    type="radio"
                    class="rating-checkbox"
                    :value="3"
                >
                <span class="text-sm text-stone-700">About 1 book every week </span>
            </label>

            <label class="rating-label" for="rating-4">
                <IconCustomPacing class="rating-svg text-indigo-500" :class="{'active': modelValue === 4}"/>
                <h2 class="rating-label-text">Custom</h2>

                <input v-model="modelValue" 
                    id="rating-4"
                    name="rating"
                    type="radio"
                    class="rating-checkbox"
                    :value="4"
                >
                <span class="text-sm text-stone-700">Don't like <i class="text-indigo-500">categorize</i> me man</span> 
            </label>
        </form>
    </div>
</template>
<script setup>
import { ref, watch } from 'vue';
import IconBlazing from '../../../svg/icon-blazing.vue';
import IconCasual from '../../../svg/icon-casual.vue';
import IconSteady from '../../../svg/icon-steady.vue';
import IconCustomPacing from '../../../svg/icon-custom-pacing.vue';

const emits = defineEmits(['set-rating']);

const modelValue = ref(null);

watch(modelValue, (newValue) => {
    emits('set-rating', newValue);
});
</script>
<style scoped>
.rating-radio-group {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    column-gap: 20px;
    row-gap: 20px;
    margin-top: 40px;
    justify-items: center;
}

.rating-label  {
    --flex-basis: 22%;
    flex-basis: var(--flex-basis);
    padding: var(--padding-sm);
    background-color: transparent;
    border-radius: var(--radius-md);
    display: grid;
    place-content: center;
    text-align: center;
    border: 1px solid var(--indigo-400);
}

@media screen and (max-width: 768px) {
    .rating-label {
        --flex-basis: 180px;
    }
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