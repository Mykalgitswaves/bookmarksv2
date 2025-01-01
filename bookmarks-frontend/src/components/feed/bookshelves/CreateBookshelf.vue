<template>
    <section class="section-wrapper">
        <h1 class="t-3xl font-medium text-slate-800">Create a bookshelf</h1>
        
        <div>
            <label for="bookshelf_title" class="title-input">
                <p>Add a title for your bookshelf</p>
                <input id="bookshelf_title" type="text" v-model="model.bookshelf_name" :maxlength="XSMALL_TEXT_LENGTH">
            </label>

            <label for="bookshelf_description" class="summary-update bookshelf">
                <p>Add a description for your bookshelf</p>
                <textarea id="bookshelf_description" v-model="model.bookshelf_description" :maxlength="MEDIUM_TEXT_LENGTH"/>
            </label>

            <div class="my-5">
                <RadioGroup 
                    id="visibility-options"
                    :options="BOOKSHELVES_VISIBLITY_OPTIONS" 
                    @updated:modelValue="(value) => { 
                        model.visibility = value
                    }"
                    >
                    <template #heading>
                        Club visibility 
                    </template>
                </RadioGroup>
            </div>

            <button 
                class="create-bookshelf-btn"
                type="button"
                @click="createAndNavigateToBookshelf(model)"
            >
                Create
            </button>

            <transition name="content">
                <div 
                    v-if="isShowingErrorMessage" 
                    class="error-message"
                >
                    <p>{{ error_message }}</p>
                </div>
            </transition>
        </div>
    </section>
</template>
<script setup>
    import { ref, reactive, toRaw } from 'vue';
    import { useRoute, useRouter } from 'vue-router'
    import { urls } from '../../../services/urls';
    import { db } from '../../../services/db';
    import { XSMALL_TEXT_LENGTH, MEDIUM_TEXT_LENGTH } from '../../../services/forms';    
    import RadioGroup from '../partials/RadioGroup.vue';
    import { BOOKSHELVES_VISIBLITY_OPTIONS } from '@/components/shared/models.js';
    
    const route = useRoute();
    const router = useRouter();
    // All shelves start as private.
    const model = reactive({
        visibility: 'private',
    });

    const error_message = ref('');
    const isShowingErrorMessage = ref(false);



    function failureFn(err){
        error_message.value = err.detail
        isShowingErrorMessage.value = true;
        setTimeout(() => {
            isShowingErrorMessage.value = false;
        }, 3000);
    }

    function successFn(data){
        const bookshelf_id = data?.bookshelf_id;
        router.push(`/feed/${route.params.user}/bookshelves/${bookshelf_id}`);
    }

    async function createAndNavigateToBookshelf(model){
        let payload = toRaw(model);
        await db.post(urls.rtc.createBookshelf(), payload, true, null, failureFn).then((res) => {
            successFn(res);
        });
    }
    
</script>
<style scoped>
    .section-wrapper {
        margin-right: auto;
        margin-left: auto;
        margin-top: var(--margin-md);
        margin-right: auto;
        margin-left: auto;
        max-width: 880px;
        width: 100%;
        padding-top: 24px;
        padding-bottom: 24px;
        padding-left: var(--padding-md);
        padding-right: var(--padding-md);
        border: 1px var(--slate-200) solid;
        border-radius: var(--radius-md);
        display: grid;
        row-gap: 40px;
    }

    .create-bookshelf-btn {
        background-color: var(--stone-200);
        color: var(--stone-600);
        border-radius: var(--radius-sm);
        padding: var(--padding-sm);
        font-size: var(--font-lg);
        width: 100%;
        transition: var(--transition-short);
    }

    .create-bookshelf-btn:hover {
        background-color: var(--stone-300);
        color: var(--stone-700);
    }

    .error-message {
        margin-top: var(--margin-md);
        background-color: var(--red-300);
        color: var(--red-800);
        padding: var(--padding-sm);
        border: 1px solid var(--red-400);
        border-radius: var(--radius-md);
    }
</style>