<template>
  <h1 class="text-center text-4xl font-medium mb-16 text-gray-700">Create an account</h1>

  <form
    class="grid grid-cols-1 w-80 h-80 gap-2 place-content-center"
  >
    <label class="text-gray-700" for="email">Enter a valid email</label>
    <input
      class="py-2 px-4 rounded-md border-2 border-indigo-200"
      v-model="formBlob.username"
      name="email"
      type="text"
      placeholder="Email"
    />

    <label class="gray-700" for="password">Enter a strong word you can remember <br><span class="text-gray-500">(password)</span></label>
    <input
      class="py-2 px-4 rounded-md border-2 border-indigo-200"
      v-model="formBlob.password"
      name="password"
      type="password"
      placeholder="Password"
    />

    <p class="mt-5 text-sm">
      By continuing, you agree to the
      <a href="#" class="text-indigo-500 underline-offset-3 underline">Self Service PSS</a> and
      <a href="#" class="text-indigo-500 underline-offset-3 underline">Privacy Policy.</a>
    </p>

    <button
      class="mt-5 px-30 py-3 bg-indigo-600 rounded-md text-indigo-100"
      type="submit"
      @click.prevent="sendData();"
    >
      Continue
    </button>
  </form>
</template>

<script>
import { useStore } from '../../stores/page'
import { toRaw } from 'vue';

export default {
  data() {
    return {
      formBlob: {
        username: '',
        password: '',
        state: null,
      },
      authStore: null
    }
  },
  methods: {
    navigate() {
      this.state.getNextPage()
    },
    async sendData() {
      try {
        const formData = toRaw(this.formBlob);
        await fetch('http://127.0.0.1:8000/api/create-login', {
          method: 'POST',
          headers: {'Content-Type': 'application/x-www-form-urlencoded'},
          body:  new URLSearchParams({
            username: formData['username'],
            password: formData['password']
            })
          })
            .then((res) => res.json())
            .then((data) => {
              console.log(data)
              document.cookie = `token=${data.access_token}`;
              this.navigate()
            });
          } catch (error) {
            // Handle any errors
            console.error('Error:', error);
          }
        }
    },
    mounted() {
      this.state = useStore()
    }
}
</script>
