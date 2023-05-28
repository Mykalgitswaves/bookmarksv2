<template>
  <div class="grid place-content-center relative">
    <div class="mt-10">
      <UserModal />

      <div class="flex flex-row gap-2 justify-start mt-5 mx-4">
        <button
          class="justify-self-end w-40 bg-indigo-600 text-indigo-100 px-6 py-2 rounded-md hover:bg-indigo-700 duration-300"
        >
          Write a review
        </button>
        <button
          class="justify-self-end w-40 bg-slate-600 text-indigo-100 px-6 py-2 rounded-md hover:bg-slate-700 duration-300"
        >
          Update status
        </button>
      </div>

      <BookReviewForm :ratings="ratings" />
      <BookReviews :reviews="reviews" />
      <RecommendedBooks :recommendations="recommendations" />
    </div>
  </div>
</template>

<script>
import MainNav from '../components/bookshelf__reader/navbar.vue'
import RecommendedBooks from '../components/bookshelf__reader/RecommendedBooks.vue'
import BookReviews from '../components/bookshelf__reader/BookReviews.vue'
import UserModal from '../components/bookshelf__reader/UserModal.vue'
import BookReviewForm from '../components/bookshelf__reader/reviews/CreateReviewForm.vue'
import IconBook from '../components/svg/icon-book.vue'

const headerMapping = {
  0: BookReviews,
  1: RecommendedBooks
}

export default {
  components: {
    MainNav,
    RecommendedBooks,
    BookReviews,
    UserModal,
    IconBook,
    BookReviewForm
  },
  data() {
    let componentState = headerMapping[0]
    let ratings = [1, 2, 3, 4, 5]
    return {
      ratings,
      recommendations: [{}, {}, {}, {}],
      reviews: [
        {
          stars: 4,
          title: 'Infinite bragging rights',
          description:
            'Read this one book, you probably dont even need to finish it. Just pop this baby down on a coffee table somewhere in plain view and watch how much undeserved attention you get from people that believe YOU actually had the discipline to read this bad boy',
          comments: [
            {
              comment:
                "This thing was pretty meaty, i read like 20 pages before i updated my hinge to talk about a niche reference about Don Gately. So far it hasn't taken me anywhere",
              stars: 4.2,
              likes: 23,
              replies: [
                {
                  comment:
                    'this is soooo dumb, like literally you are the problem here. This book was made to be read over a long period of time, not to',
                  likes: 4,
                  replies: []
                }
              ]
            }
          ]
        },
        {
          stars: 3,
          title: 'Infinite bragging rights',
          description:
            'Read this one book, you probably dont even need to finish it. Just pop this baby down on a coffee table somewhere in plain view and watch how much undeserved attention you get from people that believe YOU actually had the discipline to read this bad boy',
          comments: []
        },
        {
          stars: 2,
          title: 'Infinite bragging rights',
          description:
            'Read this one book, you probably dont even need to finish it. Just pop this baby down on a coffee table somewhere in plain view and watch how much undeserved attention you get from people that believe YOU actually had the discipline to read this bad boy'
        },
        {
          stars: 4,
          title: 'Infinite bragging rights',
          description:
            'Read this one book, you probably dont even need to finish it. Just pop this baby down on a coffee table somewhere in plain view and watch how much undeserved attention you get from people that believe YOU actually had the discipline to read this bad boy'
        },
        {
          stars: 4,
          title: 'Infinite bragging rights',
          description:
            'Read this one book, you probably dont even need to finish it. Just pop this baby down on a coffee table somewhere in plain view and watch how much undeserved attention you get from people that believe YOU actually had the discipline to read this bad boy'
        },
        {
          stars: 4,
          title: 'Infinite bragging rights',
          description:
            'Read this one book, you probably dont even need to finish it. Just pop this baby down on a coffee table somewhere in plain view and watch how much undeserved attention you get from people that believe YOU actually had the discipline to read this bad boy'
        }
      ],
      componentState
    }
  },
  methods: {
    dynamicComponentState(index) {
      this.componentState = headerMapping[index]
    }
  },
  computed: {
    currentState() {
      return this.componentState
    }
  }
}
</script>

<style scoped>
.main-dash {
  display: grid;
  grid-template-columns: 2;
}
</style>
