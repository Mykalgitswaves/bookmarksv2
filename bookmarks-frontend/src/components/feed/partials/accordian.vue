<template>
    <div class="accordian-heading">
            <h1 class="text-2xl text-slate-800 font-medium">
                <slot name="heading-text">

                </slot>
            </h1>

            <button 
                type="button"
                alt="expand-collapse"
                class="btn accordian-heading-btn large"
                @click="emit('clicked-chevron', !props.expanded)"
            >
                <IconChevron />
            </button>
        </div>
</template>
<script setup>
    import IconChevron from '../../svg/icon-chevron.vue';
    const props = defineProps({
        expanded: {
            type: Boolean,
            required: true,
        }
    });

    const emit = defineEmits(['clicked-chevron'])
</script>
<style scoped>
    .accordian-heading {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
    }
</style>