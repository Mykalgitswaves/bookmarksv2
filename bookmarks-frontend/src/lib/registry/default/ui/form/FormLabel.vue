<template>
  <Label
    :class="cn(
      error && 'text-destructive',
      props.class,
    )"
    :for="formItemId"
  >
    <slot />
  </Label>
</template>
<script lang="ts" setup>
import type { HTMLAttributes } from 'vue';
import type { LabelProps } from 'reka-ui';
import { cn } from '@/lib/utils';
import { Label } from '@/lib/registry/default/ui/label';
import { useFormField } from './useFormField.ts';

const props = defineProps<LabelProps & { class?: HTMLAttributes['class'] }>()

const { error, formItemId } = useFormField()
</script>