<template>
    <div class="flex gap-2 justify-center items-center">
        <input id="bookcount" 
        name="bookcount" 
        type="number" 
        class="input-number short"
        v-model="form.num_books"
        />

        <label for="bookcount" class="display-block italic text-stone-600 text-sm">
            book every
        </label>   

        <input type="number" 
            class="input-number short" 
            v-model="form.num_time_period"
        />

        
            <label class="select-1" for="pace">
                <span class="hidden">pace</span>

                <select class="" name="pace" id="pace" v-model="form.time_period">
                    <option v-for="(option, index) in selectOptions" 
                        :key="index" 
                        :value="option"
                    >
                        {{ option }}
                    </option>
                </select>
            </label>
        
    </div>
</template>
<script setup>
import { watch, ref } from 'vue';
import { BookClub } from '../models/models';

const selectOptions = Object.values(BookClub.paceIntervals)

const form = ref({
    num_books: 1,
    num_time_period: 1,
    time_period: selectOptions[1],
    name: '',
});

const emit = defineEmits(['update-form-data'])

watch(form, (newValue) => {
    if (newValue) {
        emit('update-form-data', newValue)
    }
})
</script>