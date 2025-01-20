<template>
    <div v-if="update.response?.length || update.quote?.length" class="container questions">
        <div v-if="update.quote" class="quote">
            <div class="my-2">
                <p class="text-start">
                    {{ update.quote }}
                </p>
            </div>
        </div>

        <div v-if="update.response">
            <div class="my-3 text-lg question-border px-5 py-5 w-100 box-btn justify-between items-center">
                <div class="text-start">
                    <span class="block fancy">Your update</span>

                    <span class="block text-slate-400 text-start">{{ update.response }}?</span>

                </div>
            </div>
        </div>
    </div>

    <div v-if="!update.response?.length" style="text-align: center;">
        <h2 class="heading">You haven't added any responses</h2>

        <p class="subheading">Click 
            <button type="button" 
                class="underline text-indigo-500"
                @click="emit('go-to-edit-section')"    
            >here
            </button> to add some responses
        </p>
    </div>
</template>
<script setup>
const props = defineProps({
    update: {
        type: Object,
        required: true,
    }
});

const emit = defineEmits(['go-to-edit-section']);
</script>
<style scoped>
.quote {
    padding-left: var(--padding-md);
    padding-right: var(--padding-md);
    padding-top: var(--spacing-sm);
    padding-bottom: var(--spacing-sm);
    margin-bottom: var(--spacing-sm);
    margin-right: var(--spacing-md);
    margin-left: var(--spacing-md);
    font-style: italic;
    background-color: var(--stone-50);
    color: var(--stone-800);
    border-radius: var(--radius-sm);
}
</style>