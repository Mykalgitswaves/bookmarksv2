<!-- eslint-disable vue/no-parsing-error -->
<template>
  <section class="login-wrapper">

    <!-- <h1 class="text-center text-xl mb-5 fancy text-indigo-400">Hardcoverlit</h1> -->
    <h1 class="text-center text-4xl mb-16 text-stone-600">Log in</h1>

    <form
      class="grid grid-cols-1 h-80 gap-2 place-content-center px-5"
      @submit.prevent="submitForm()"
      method="POST"
    >
      <label class="gray-700" for="login_username">Enter your username</label>

      <input
        type="username"
        class="py-2 px-4 rounded-md border-2 border-indigo-200"
        v-model="formBlob.username"
        name="username"
        id="login_username"
        placeholder="Email"
      />

      <label class="gray-700" for="login_password">Password</label>

      <input
        type="password"
        class="py-2 px-4 rounded-md border-2 border-indigo-200"
        v-model="formBlob.password"
        name="password"
        id="login_password"
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
      class="text-xs text-center mt-5 px-5 py-2 mx-auto rounded-md bg-red-600 text-red-100"
      v-if="errorMessage"
    >
      Username or password invalid please try a different login
    </span>
</section>
</template>

<script setup>
import { ref, toRaw } from 'vue';
import { useRouter } from 'vue-router';
import { urls, navRoutes } from '../services/urls';

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
    const response = await fetch(urls.login, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
      },
      // convert this from proxy toRaw
      body: formData,
    });

      if (!response.ok) { // Check if the response status is not OK (not 200-299)
        errorMessage.value = true;
        setTimeout(() => {
        errorMessage.value = false;
      }, 2000);
    }
    else {
      const data = await response.json();
      console.log(data);

      const user_id = data.user_id;
      const token = `token=${data.access_token}`;
      document.cookie = token;
      router.push(navRoutes.toLoggedInFeed(user_id));
    }
  
} catch (error) {
  console.error(error);
  message.value = error.detail || error.message; // Use error message if detail is not available
  errorMessage.value = true;

  setTimeout(() => {
    errorMessage.value = false;
  }, 2000);
}
}
</script>
