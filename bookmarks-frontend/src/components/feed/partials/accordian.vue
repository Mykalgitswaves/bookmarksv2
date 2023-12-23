<template>
    <div class="accordian-heading">
            <h1 class="text-2xl text-slate-800 font-medium">
                <slot name="heading-text">

                </slot>
            </h1>

            <button 
                type="button"
                alt="expand-collapse"
                class="accordian-heading-btn"
                :class="{'collapsed-chevron': props.expanded === true}"
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
    
    .accordian-heading-btn {
        background-color: var(--slate-50);
        transition: all 250ms ease-in;
        padding: 4px;
        border-radius: 4px;
    }

    .accordian-heading-btn:hover {
        background-color: var(--slate-300);
    }

    .collapsed-chevron svg {
        transform: rotate(180deg);
    }

</style>