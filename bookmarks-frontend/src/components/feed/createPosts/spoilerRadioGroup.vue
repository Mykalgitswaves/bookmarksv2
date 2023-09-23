<template>
    <p class="mb-1 italic text-slate-600 text-small">spoilers?</p>
        <div class="radio-group">
            <KeepAlive>
                <label
                    class="radio-select flex"
                    :for="`radio-group-${modelObject.id}-id`" 
                    v-for="(bool, index) in [true, false]"
                    :key="index"
                >
                    <input
                        :id="`radio-group-${modelObject.id}-id`"
                        type="radio"
                        :value="bool"
                        :name="`radio-group-${modelObject.id}-bool`"
                        v-model="modelObject.is_spoiler"
                        @change="emit('is-spoiler-event', modelObject)"
                    >
                    <span class="inline">{{ bool === true ? 'yes' : 'no' }}</span>
                </label>
            </KeepAlive>
        </div>
</template>
<script setup>
import { defineEmits, computed } from 'vue'
const props = defineProps({
    modelObject: Object
})

const modelObject = computed(() => (props.modelObject))

const emit = defineEmits();


</script>