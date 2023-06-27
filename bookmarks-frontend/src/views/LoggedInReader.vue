<template>
  <TopNav :profilePicture="profilePicture"/>
  <div class="bg-gray-200 main-layout">
    <h2 class="pt-4 text-2xl font-medium text-slate-600">Recommended Works</h2>  
    
    <KeepAlive>
      <ReviewCard 
        v-for="(c, index) in cards" 
        :key="index" 
        :placeholderBookImg="placeholderBookImg" 
      />
    </KeepAlive>
  </div>
  <FooterNav/>
</template>

<script>
  import TopNav from '@/components/feed/topnav.vue';
  import ReviewCard from '@/components/feed/ReviewCard.vue';
  import FooterNav from '@/components/feed/footernav.vue'
  import profilePicture from '@/assets/profileimage.jpg'
  import placeholderBookImg from '@/assets/infiniteJest.png'

// const headerMapping = {
//   0: BookReviews,
//   1: RecommendedBooks
// }

export default {
  components: {
    TopNav,
    ReviewCard,
    FooterNav
  },
  data() {
    // let componentState = headerMapping[0]
    let cards = [1, 2, 3, 4, 5]
    return {
      profilePicture,
      placeholderBookImg,
      cards
    }
  },
  methods: {
    // dynamicComponentState(index) {
    //   this.componentState = headerMapping[index]
    // }
  },
  computed: {
    // currentState() {
    //   return this.componentState
    // }
  }
}
</script>
<style scoped>

.main-layout {
  min-height: 80vh;
  padding: 1.25rem;
  display: grid;
  grid-template-columns: 1;
  grid-auto-rows: minmax(min-content, max-content);
  gap: 2ch;
}



</style>

