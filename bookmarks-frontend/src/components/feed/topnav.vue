<template>
  <nav class=" relative">
    <div class="navbar-p">
      <Logo />
      <div class="flex reverse"> 
        <button class="ml-5 text-indigo-800"
          type="button"
          alt="show logout menu"
          @click="isMenuShowing = !isMenuShowing"
        >
          <IconMenu />
        </button>

        <img class="profile-image border-solid 
        border-indigo-600 border-2 ml-5"
          :src="profilePicture"
          alt="profileImage"  
        />
        
        <div class="navbar-text">
            <p class="text-slate-800 font-semibold text-xl">{{ user.fullName }}</p>
            <p><span v-for="(genre, index) in user.genres" :key="index">{{ genre + helpersCtrl.commanator(index, user.genres.length)}}</span></p>
        </div>
      </div>
    </div>

    <div 
      v-if="isMenuShowing"
      class="top-menu-wrapper bg-slate-200 rounded-md shadow-lg" 
    >
      <button 
        class="bg-slate-900 text-slate-200 px-3 py-2 rounded-md"
        type="button" 
        alt="logout button"
        @click="logout()"
      >
        Logout
      </button>
    </div>
  </nav>
</template>

<script setup>
    import { defineProps, toRefs, computed, ref } from 'vue'
    import { useNavigationStore } from '@/stores/navigation.js';
    import { helpersCtrl } from '@/services/helpers.js' 
    import IconMenu from '../svg/icon-menu.vue';
    import Logo from '@/components/svg/icon-logo.vue';
    import router from '../../router';

    const store = useNavigationStore();
    const props = defineProps({
        profilePicture: String,
    })

    function logout(){
    router.push('/')
  }

    const { profilePicture } = toRefs(props)
    const isMenuShowing = ref(false);

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

.top-menu-wrapper {
  position: absolute;
  top: 45vh;
  right: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
  padding: 2rem;
  width: 300px;
  text-align: center;
  border-bottom-left-radius: 4px;
}

</style>