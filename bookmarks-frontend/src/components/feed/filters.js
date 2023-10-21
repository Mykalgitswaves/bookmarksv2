import { reactive } from 'vue';

export const filterOptions = reactive([
    {
      pk: 1,
      filter: 'comparison',
      is_active: false,
    },
    {
      pk: 2,
      filter: 'review',
      is_active: false,
    },
    {
      pk: 3,
      filter: 'update',
      is_active: false,
    } 
  ])