<!-- eslint-disable vue/no-parsing-error -->
<template>
  <h1 class="text-center text-4xl font-medium mb-16">Log in</h1>

  <form
    class="grid grid-cols-1 h-80 gap-2 place-content-center px-5"
    @submit.prevent="submitForm()"
    method="POST"
  >
    <label class="gray-700">Enter your email</label>
    <input
      class="py-2 px-4 rounded-md border-2 border-indigo-200"
      v-model="formBlob.username"
      name="username"
      type="email"
      placeholder="Email"
    />

    <label class="gray-700">Password</label>
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
    >
      Submit
    </button>
  </form>

  <span
    class="text-xs text-center mt-5 px-5 py-2 rounded-md bg-red-600 text-red-100"
    v-if="errorMessage"
  >
    Username or password invalid <br />please try a different login
  </span>
  <div class="grid mt-10 text-center">
  <RouterLink to="/create-user">
    <button type="button" class="my-2">
        <span class="italic">For readers</span><br>
        <span class="text-md text-indigo-600 font-semibold underline underline-offset-2">
        create an account
        </span>
    </button>
  </RouterLink>
</div>
</template>

<script setup>
import {ref, toRaw } from 'vue';
import { useRouter } from 'vue-router';

const message = ref('');
const formBlob = ref({
  username: '',
  password: ''
});
const errorMessage = ref(false);
const router = useRouter();

// Convert this to a controller function to use elsewhere.
async function submitForm() {
  const formData = new URLSearchParams();

  formData.append('username', toRaw(formBlob.value.username));
  formData.append('password', toRaw(formBlob.value.password));
  
  try {
    await fetch('http://127.0.0.1:8000/api/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
      },
      // convert this from proxy toRaw
      body: formData,
    }).then((res) => res.json())
    .then((data) => {
      const uuid = data.user.uuid
      const token = `token=${data.token.access_token}`;
      document.cookie = token;
      return router.push(`/feed/${uuid}/all`);
    })
  } catch(error) {
      console.error(error)
    //   message.value = error.detail;
    //   errorMessage.value = true
      
    //   setTimeout(() => {
    //     return (errorMessage.value = false)
    //   }, 2000)
    // console.error(error);
  }
}
</script>
