<template>
  <span
    v-bind="$attrs"
    v-for="index in stars"
    :key="index"
    class="icon-star text-indigo-400"
    style="left: calc((100% / ${stars}) * ${index - 1})"
  >
    <svg
      class="inline"
      xmlns="http://www.w3.org/2000/svg"
      height="20"
      fill="currentColor"
      viewBox="0 96 960 960"
      width="20"
    >
      <path
        d="m323 851 157-94 157 95-42-178 138-120-182-16-71-168-71 167-182 16 138 120-42 178Zm-90 125 65-281L80 506l288-25 112-265 112 265 288 25-218 189 65 281-247-149-247 149Zm247-355Z"
      />
    </svg>
  </span>
</template>

<script>
export default {
  props: {
    stars: {
      type: Array,
      required: true
    }
  }
}
</script>
