<template>
  <nav>
    <div class="navbar-p border-solid border-indigo-500 border-b-2">
      <Logo />
      <div> 
        <img class="profile-image border-solid 
        border-indigo-600 border-2"
          :src="profilePicture"
          alt="profileImage"/>
      </div>
    </div>

    <Component 
        :is="navigationMapping.component"
        v-bind="navigationMapping.props"
    />
    <div class="tab-group">
        <button
            class="tab-btn text-xl" 
            :class="isFeedTabActive === true ? 'active' : ''"
            @click="isFeedTabActive = !isFeedTabActive" 
        >Feed</button>

        <button 
            class="tab-btn text-xl"
            :class="isBookshelfTabActive === true ? 'active' : ''"
            @click="isBookshelfTabActive = !isBookshelfTabActive" 
        >Bookshelf</button>
    </div>
  </nav>
</template>

<script setup>
    import { defineProps, toRefs, computed, ref } from 'vue'
    import { useNavigationStore } from '@/stores/navigation.js';

    import Logo from '@/components/svg/icon-logo.vue';
    import feedSubNav from '@/components/feed/navigation/feedSubNav.vue'

    const store = useNavigationStore();
    const props = defineProps({
        profilePicture: String,
    })

    let isFeedTabActive = ref(true);
    let isBookshelfTabActive = ref(false);

    const dynamicSubNav = {
        0: {
            component: feedSubNav,
            props: {
                profilePicture: props.profilePicture
            }
        } 
    }

    const { profilePicture } = toRefs(props)

    const navigationMapping = computed(() => {
       return dynamicSubNav[store.navState]
    })
</script>

<style scoped>
.navbar-p {
  padding: 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center; 
}

.profile-image {
  height: 3rem;
  border-radius: 50%;
  opacity: 1;
  cursor: pointer;
}

.tab-group {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(2, minmax(160px, 200px));
    justify-content: center;
}

.tab-btn {
    color: #718096;
}

.active {
    border-bottom: solid .25rem #5A67D8;
    color: #5A67D8;
}

</style>