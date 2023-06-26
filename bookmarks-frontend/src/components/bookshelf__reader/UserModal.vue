<template>
  <div class="bg-slate-50 rounded-md h-auto py-4 px-4 relative overflow-clip">
    <img
      class="border-solid border-indigo-300 border-2 absolute top-2 left-2 rounded-[50%] h-28 w-28"
      src="../../assets/profileimage.jpg"
    />

    <div class="grid grid-cols-1 gap-6 ml-32">
      <div>
        <p class="text-2xl font-semibold text-slate-800">
          Aaron Wordnerd III&emsp13;<span class="font-light">(He/Him)</span>
        </p>
        <p class="text-lg text-slate-600">Fiction, Poetry, Contemporary Scat/Slam Verses</p>
      </div>

      <div class="flex flex-row gap-3 mt-4 w-100 justify-start">
        <button
          class="inline-block text-xl text-slate-400 rounded-md cursor-pointer"
          @click="dynamicComponentState(0)"
        >
          <span class="flex flex-row align-middle justify-center"><IconBook /> Books </span>
        </button>

        <button
          class="inline-block text-xl text-indigo-600 rounded-md cursor-pointer underline"
          @click="dynamicComponentState(1)"
        >
          Reviews
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {}
</script>
