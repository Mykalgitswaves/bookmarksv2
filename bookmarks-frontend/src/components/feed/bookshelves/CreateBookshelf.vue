<template>
    <section class="section-wrapper">
        <h1 class="t-3xl font-medium text-slate-800">Create a bookshelf</h1>
        
        <div>
            <label for="bookshelf_title" class="title-input">
                <p>Add a title for your bookshelf</p>
                <input id="bookshelf_title" type="text" v-model="model.bookshelf_name">
            </label>

            <label for="bookshelf_description" class="summary-update bookshelf">
                <p>Add a description for your bookshelf</p>
                <textarea id="bookshelf_description" v-model="model.bookshelf_description"/>
            </label>

            <button 
                class="create-bookshelf-btn"
                type="button"
                @click="createAndNavigateToBookshelf(model)"
            >
                Create
            </button>
        </div>
    </section>
</template>
<script setup>
    import { reactive, toRaw } from 'vue';
    import { useRoute, useRouter } from 'vue-router'
    import { urls } from '../../../services/urls';
    import { db } from '../../../services/db';
    const route = useRoute();
    const router = useRouter();
    const model = reactive({});

    async function createAndNavigateToBookshelf(model){
        let payload = toRaw(model);
        db.post(urls.rtc.createBookshelf(route.params.user), payload, true).then((res) => {
            console.log(res.data);
            // router.push()
        })
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
</style>