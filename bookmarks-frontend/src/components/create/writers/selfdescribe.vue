<template>
  <div class="container grid place-content-center min-w-[280px] max-w-[500px]">
      <form class="grid grid-cols-1 gap-5">
        <h3 class="text-3xl italic">
          Spare no details<span class="text-xl normal">
            - Hemmingway <span class="text-sm">(we think?)</span></span
          >
        </h3>

      <span class="block">
        <label 
            class="block font-semibold" 
            for="first_name">Your full name</label>
        <input 
            class="w-80 px-4 py-2 mt-2 
            rounded-md border-2 border-indigo-200"
            type="text" 
        />
      </span>

      <span class="block">
        <label class="block font-semibold" for="first_name">Describe your writing style</label>
        <textarea
          rows="4"
          class="w-[100%] px-4 py-2 mt-2 rounded-md border-2 border-indigo-200"
          type="text"
        />
      </span>
      <p class="font-semibold">Which of these words resonate with your writing style (if any)</p>
      <div class="grid grid-cols-5 gap-3">
            {# TODO: Make grid auto columns #}
            <span 
                class="col-span-1 rounded-md border-solid 
                border-2 border-slate-400 py-2 px-2
                hover:border-indigo-500 duration-300 nowrap"
                v-for="(adjective, index) in adjectives"
                :key="index"
                @click="addToFormState(adjective)"
            >
            + {{ adjective }}
            </span>
        </div>
        <button 
            class="mt-5 px-36 py-3 bg-indigo-600 rounded-md text-indigo-100"
            type="submit"
            @click="navigate"
        >
            Continue
        </button>
    </form>
  </div>
</template>
<script>

import { useStore } from '../../../stores/page.js'

export default {
    data() {
        return {
            adjectives: [
                'Serious',
                'Contemporary',
                'Explorative',
                'GenreLess',
                'Historic',
                'Fiction',
                'Romantic',
                'Adventurous',

            ]
        }
    },
    methods: {
    navigate() {
        this.state.getNextPage()
        console.log(this.state.page)
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
  font-weight: 300;
}

.nowrap {
 white-space: nowrap;
}
</style>
