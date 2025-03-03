<template>
<div class="create-menu">
    <Collapsible>
        <CollapsibleTrigger class="space-y-2 gap-2 flex items-center text-sm fancy text-stone-600 hover:bg-stone-100 w-100 p-2">
            <IconLucideAdd style="width: 20px; height: 20px;"/> 
            Create
        </CollapsibleTrigger>
        <CollapsibleContent class="grid">
            <Seperator orientation="horizontal" class="mb-2"/>
            
            <button 
                type="button" 
                class="ml-2 btn btn-tiny text-xs btn-specter fancy text-start" 
                :class="{'nav-active': $route.path.includes('review')}"
                alt="create a post"
                @click="$router.push(navRoutes.toCreatePost($route.params.user, 'review'))"
            >
                Review
            </button>

            <button 
                type="button" 
                class="ml-2 btn btn-tiny text-xs btn-specter fancy text-start" 
                :class="{'nav-active': $route.path.includes('update')}"
                alt="create a post"
                @click="$router.push(navRoutes.toCreatePost($route.params.user, 'update'))"
            >
                Update
            </button>

            <button 
                type="button" 
                class="ml-2 btn btn-tiny text-xs btn-specter fancy text-start" 
                :class="{'nav-active': $route.path.includes('comparison')}"
                alt="create a post"
                @click="$router.push(navRoutes.toCreatePost($route.params.user, 'comparison'))"
            >
                Comparision
            </button>

            <button
                type="button" 
                class="btn btn-tiny text-xs btn-specter fancy text-start" 
                alt="create a post"
                @click="$router.push(navRoutes.toCreateClubPage($route.params.user))"
            >
                Bookclub
            </button>

            <button 
                type="button" 
                class="btn btn-tiny text-xs btn-specter fancy text-start" 
                alt="create a post"
                @click="$router.push(navRoutes.toBookshelvesCreate($route.params.user))"
            >
                Bookshelf
            </button>

            <Seperator orientation="horizontal" class="mt-2 desktop-only"/>
        </CollapsibleContent>
    </Collapsible>
</div>
</template>
<script setup>
import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger,
} from '@/lib/registry/default/ui/collapsible';
// lucide
import Seperator from '@/lib/registry/default/ui/seperator/Seperator.vue';
import IconLucideAdd from '../../svg/icon-lucide-add.vue';
import { navRoutes } from '@/services/urls';
</script>