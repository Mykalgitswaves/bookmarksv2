<template>

</template>
<script setup>
    import { ref, onMounted } from 'vue';
    import { db } from '../../../services/db';
    import { urls } from '../../../services/urls';
    import { useRoute } from 'vue-router';
    
    const props = defineProps({
        shelfType: {
            type: String,
            required: true,
        },
    });
    const route = useRoute();
    const bookshelves = ref([]);

    async function getBookshelvesForSection(){
        let url = '';
        if(route.params.shelfType === 'created_bookshelves') {
            url = urls.rtc.getBookshelvesCreatedByUser(route.params.user);
        } else {
            url = urls.rtc.getShelvesBySection(route.params.shelfType);
        }
        await db.get(url).then((res) => {
            bookshelves.value = res.data;
        });
    }

    onMounted(async () => {
        await getBookshelvesForSection();
    });
</script>