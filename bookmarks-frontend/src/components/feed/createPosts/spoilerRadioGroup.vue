<template>
    <p class="mb-2 italic text-slate-600">spoilers?</p>
        <div class="radio-group">
            <label
                class="radio-select flex"
                :for="`radio-group-${bool}`" 
                v-for="(bool, index) in [true, false]"
                :key="index"
            >
                <input
                    :id="`radio-group-${bool}`"
                    type="radio"
                    :value="bool"
                    name="radio-group-bool"
                    v-model="isSpoilers"
                    @change="emit('is-spoiler-event', isSpoilers)"
                >
                <span class="inline">{{ bool === true ? 'yes' : 'no' }}</span>
            </label>
        </div>
</template>
<script setup>
import { defineEmits } from 'vue'
let isSpoilers = null
const emit = defineEmits();


</script>