<template>
    <div class="h-screen w-screen grid place-content-center relative">
        <Component :is="createFormState"/>
    </div>
</template>
<script>
    import createWriterSelfDescribe from '@/components/create/writers/selfdescribe.vue';
    import createWriterUploadWork from '@/components/create/writers/uploadwork.vue';
    import createWriterFinal from '@/components/create/writers/finalize.vue';

    //For component transitions on a page
    import { computed } from 'vue'
    import { useStore } from '../stores/page.js'

    const writerFormMapping = {
        1: createWriterSelfDescribe,
        2: createWriterUploadWork,
        3: createWriterFinal
    }

    export default {
        data(){
            return {
                createFormState: null,
                state: null
            }
        },
        methods: {
            getNextPage() {
                const state = useStore()
                state.getNextPage()
            },
            getPrevPage() {
                const state = useStore()
                state.getPrevPage()
            }
        },
        mounted() {
            const state = useStore()
            this.state = state
            this.createFormState = computed(() => writerFormMapping[state.page])
        }
    }
</script>