<template>
<div :class="alertVariantCss()">
    <component class="icon" :is="TEXT_ALERT[variant].icon" />

    <div>
        <h3 class="alert-heading">
            <slot name="alert-heading"></slot>
        </h3>

        <p class="alert-content">
            <slot name="alert-content"></slot>
        </p>
    </div>
</div>
</template>
<script setup>
import { TEXT_ALERT } from './textAlert.js';

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
    }
});

const alertVariantCss = () => (`text-alert ${props.variant}`);
</script>
<style scoped>
 .text-alert {
    max-width: 768px;
    padding: 8px 14px;
    border-radius: 8px;
    border: 1px solid var(--stone-300);
    display: grid;
    grid-template-columns: 40px 1fr;
    column-gap: 14px;
    margin-left: auto;
    margin-right: auto;
    
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
    
    .alert-content {
        padding-top: .5rem;
        font-size: var(--font-sm);
        color: var(--stone-500);
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
        background-color: var(--orange-100);
        border-color: var(--orange-500);

        svg {
            color: var(--orange-400);
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