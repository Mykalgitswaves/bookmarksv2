<template>
  <nav class="shadow-sm">
    <div class="navbar-p border-solid border-indigo-500 border-b-2">
      <Logo />
      <div class="flex reverse"> 
        <img class="profile-image border-solid 
        border-indigo-600 border-2 ml-5"
          :src="profilePicture"
          alt="profileImage"/>
          
        <div class="navbar-text">
            <p class="text-slate-800 font-semibold text-xl">{{ user.fullName }} Bookmarks</p>
            <p><span v-for="(genre, index) in user.genres" :key="index">{{ genre + helpersCtrl.commanator(index, user.genres.length)}}</span></p>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
    import { defineProps, toRefs, computed, ref } from 'vue'
    import { useNavigationStore } from '@/stores/navigation.js';
    import { helpersCtrl } from '@/services/helpers.js' 

    import Logo from '@/components/svg/icon-logo.vue';

    const store = useNavigationStore();
    const props = defineProps({
        profilePicture: String,
    })


    const { profilePicture } = toRefs(props)

    const user = {
        fullName: 'Aaron Wordnerd III\'s ',
        genres: ['Fiction', 'Poetry', 'contemporary']
    };
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
    border-bottom: solid .25rem #dbdada;
    padding-bottom: .5rem;
}

.active {
    border-bottom: solid .25rem #5A67D8;
    color: #5A67D8;
}

.reverse {
    flex-direction: row-reverse;
}

@media only screen and (max-width: 768px)  {
  .navbar-text {
      display: none;
  }
}

</style>