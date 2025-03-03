<template>
    <!-- Top nav bar that is absolute positioned, for making posts and filtering posts -->
    <div class="feed-menu-nav" role="menubar">
      <Popover>
        <PopoverTrigger class="btn btn-small fancy flex gap-2 items-center">
          <IconAdd style="width: 20px; height: 20px;"/> Create post
        </PopoverTrigger>
        <PopoverContent class="max-w-[250px] grid row-gap-2">
          <button  
            v-for="(option, index) in postOptions"
              :key="index"
              type="button"
              class="btn btn-tiny fancy btn-specter"
              @click="navigate(createPostBaseRoute, option)"  
            >
              {{ option }}
            </button>
        </PopoverContent>
      </Popover>
    </div>
</template>
<script setup>
import { reactive } from 'vue';
import { navigate } from './createPostService';
import IconAdd from '../svg/icon-lucide-add.vue';
import { Popover, PopoverContent, PopoverTrigger } from '@/lib/registry/default/ui/popover';

const props = defineProps({
    user: {
        type: String,
        required: true,
    },
});

const createPostBaseRoute = `/feed/${props.user}/create`;
const postOptions = ['review', 'update', 'comparison'];
// Used to show and hide modals.
const modals = reactive({
  selectDropdown: false,
  filterPopout: false,
});

function closeModal(reactiveKey) {
  modals[reactiveKey] = false;
}
</script>
<style scoped>
  .feed-menu-nav {
    position: sticky;
    display: flex;
    column-gap: 10px;
    justify-content: space-between;
    padding: 10px;
    top: 40px;
  }

  .text-white {
    color: white;
  }
</style>