<template>
    <form class="container grid place-content-center gap-3 max-w-[600px] min-w-[280px]" action="">
        <p class="text-lg font-semibold">If you're comfortable share a page, a chapter or an entire work of yours
            <br><span class="font-light text-slate-600 italic text-sm">We don't take ownership of anything you write, it is used to classify your work and help us connect you with a larger audience. <span class="text-indigo-600 cursor-pointer underline">Learn more about how our recommendation process works</span></span>
        </p>
        <span class="block mx-auto text-center mt-10">
            <label class="block font-semibold text-lg text-slate-800" for="">{{ inputText }}</label>
            <input 
            @mouseout="changeInputText"
            class="mt-2 py-4 px-4 border-solid border-indigo-300 border-2 rounded-md" type="file">
        </span>
        
        <span class="mt-20">
            <label class="block font-semibold" for="">Or copy and paste!</label>
            <textarea 
                class="w-[100%] mt-2 border-solid border-indigo-300 border-2 rounded-md" 
                name="" id="" cols="30" rows="10"
            />
        </span>
        <p 
            class="cursor-pointer text-indigo-800 
            font-semibold text-center" 
            @click="isStanceShowing = !isStanceShowing"
        >
            Our stance on plagiarism:
                <span 
                    class="w-[80%] text-slate-800 normal" v-if="isStanceShowing">
                    All works submitted are cross referenced to ensure that they do not appear as published works under a different authors name. For this reason it is crucial that the name associated with any digital or print publishing matches your accounts information. This process happens after submission so make sure before you finalize your profile you change your name and links to selected works if they do not match!
                </span>
        </p>
        <button 
            class="mt-5 px-36 py-4 bg-indigo-600 rounded-sm text-indigo-100"
            type="submit"
            @click="navigate"
        >
            Continue
        </button>
    </form>
</template>

<script>
    import { useStore } from '../../../stores/page.js';

    export default {
        data() {
            return {
                inputFieldTextArr: ['Magnum Opus\'s welcome', 'A page, maybe a chapter', 'If you\'re worried about other people reading it it\'s prolly fire', 'Perfection is the bane of progress'],
                inputText: 'Magnum Opus\'s welcome',
                index: 0,
                isStanceShowing: false
            }
        },
        methods: {
            changeInputText() {
                
                // todo set interval to change input text value while users are on page. 
                this.index++
                if(this.index === this.inputFieldTextArr.length) {
                    this.index = 0
                }
                this.inputText = this.inputFieldTextArr[this.index]
            },
            navigate(){
                this.state.getNextPage()
            }
        },
        mounted() {
            this.state = useStore()
        }
    }
</script>

<style scoped>
    .normal {
        font-style: normal !important;
        font-weight: 400;
    }
</style>