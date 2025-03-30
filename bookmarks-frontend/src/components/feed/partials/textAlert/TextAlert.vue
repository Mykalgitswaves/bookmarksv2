<template>
<div :class="alertVariantCss()">
    <component class="icon" :is="TEXT_ALERT[iconOverride ?? variant].icon"/>

    <div>
        <div class="flex" :class="{'justify-between items-center': isCollapsible}">
            <h3 class="alert-heading">
                <slot name="alert-heading"></slot>
            </h3>

            <button v-if="isCollapsible" class="btn btn-subtle btn-tiny pt-0" :class="{'one-80-deg': !isCollapsed}" @click="isCollapsed = !isCollapsed">
                <IconChevron/>
            </button>
        </div>

        <p class="alert-content" v-if="isCollapsed">
            <slot name="alert-content"></slot>
        </p>
    </div>
</div>
</template>
<script setup>
import { TEXT_ALERT } from './textAlert.js';
import { ref } from 'vue';
import IconChevron from '../../../svg/icon-chevron.vue';

const props = defineProps({
    variant: {
        type: String,
        required: false,
        default: TEXT_ALERT.default,
        validator(props, variant) {
            // if a variant is provided, check it, otherwise resort to
            // default which we know is true.
            return variant ? TEXT_ALERT.variants.includes(variant) : true;
        },
    },
    isCollapsible: {
        type: Boolean,
        required: false,
        default: () => false,
    },
    iconOverride: {
        type: String
    }
});

const alertVariantCss = () => (`text-alert ${props.variant}`);
const isCollapsed = ref(true);
</script>
<style scoped>


 .text-alert {
    max-width: 768px;
    padding: 8px 14px;
    border-radius: 8px;
    border: 1px solid var(--stone-300);
    display: grid;
    column-gap: 14px;
    margin-left: auto;
    margin-right: auto;
    grid-template-columns: 30px 1fr;
    
    svg {
        max-width: 40px;
        height: auto;
        align-self: start;
        margin-top: 10px;
    }

    .alert-heading {
        font-size: var(--font-lg);
        line-height: 1.5;
        font-family: var(--fancy-script);
    }
    
    @starting-style {
        .alert-content {
            opacity: 0;
        }
    }

    .text-alert:has(svg) {
        grid-template-columns: 40px 1fr;
    }

    .alert-content {
        padding-top: .5rem;
        font-size: var(--font-sm);
        color: var(--stone-500);
        transition: all 150ms ease-in-out;
    }

    &.info {
        background-color: var(--blue-50);
        border-color: var(--blue-500);
        
        svg {
            color: var(--blue-500)
        }

        .alert-heading {
            color: var(--stone-600);
        }
    }

    &.warning {
        background-color: var(--red-100);
        border-color: var(--red-500);

        svg {
            color: var(--red-400);
        }

        .alert-heading {
            color: var(--stone-600);
        }
    }

    &.error {
        background-color: var(--red-100);
        border-color: var(--red-500);

        .alert-heading {
            color: var(--red-700);
        }
    }
 }

 
</style>