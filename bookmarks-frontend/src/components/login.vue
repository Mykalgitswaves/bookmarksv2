<template>
    <h1 class="text-center text-4xl font-medium mb-16">Log in</h1>

    <form 
      class="grid grid-cols-1 w-80 h-80 gap-2 place-content-center"
      action="submitForm"
      method="POST"
    >
      <label class="gray-700">Enter your email</label> 
      <input
        class="py-2 px-4 rounded-md
        border-2 border-indigo-200" 
        :v-model="formBlob.name"
        name="fullname"
        type="text"
        placeholder="Email"
      /> 

      <label class="gray-700">Password</label> 
      <input
        class="py-2 px-4 rounded-md
        border-2 border-indigo-200" 
        :v-model="formBlob.password"
        name="password"
        type="text"
        placeholder="Password"
      /> 
      
      <p class="mt-5 text-sm">By continuing, you agree to the <a href="#" class="text-indigo-500 underline-offset-3 underline">Self Service PSS</a>
        and <a href="#" class="text-indigo-500 underline-offset-3 underline">Privacy Policy.</a></p> 

      <button
        class="mt-5 px-30 py-3 bg-indigo-600
        rounded-md text-indigo-100" 
        type="submit"
        @click.prevent="submitForm"
      >Submit</button>  
    </form>

    <span class="text-xs text-center mt-2
      px-5 py-2 rounded-md bg-red-600
      text-red-100"
      v-if="errorMessage"
      >
      Username or password invalid <br>please try a different login
    </span>  

    <RouterLink to="/create-user">or create an account</RouterLink>
</template>

<script>
  import { toRaw } from 'vue';
  import { RouterLink } from 'vue-router';

  export default {

    data() {
      return {
        message: null,
        token: null,
        formBlob: {},
        errorMessage: false
      }
    },
    methods: {
      async submitForm() {
          await fetch('http://http://127.0.0.1:8000/api/login', {
            method: 'POST',
            headers: {
              Accept: 
                'application.json',
                'Content-Type': 'application/json',
                'X-CSRFToken': this.token
              },
              // convert this from proxy toRaw
            body: JSON.stringify(this.formBlob),
            cache: 'default'  
          }).then(response => {
              // Handle the response
              this.errorMessage = false;
              console.log(response)
              return response
          })
          .catch(error => {
            console.log(error)
            this.errorMessage = true;
            // hide error message after 
            setTimeout(() => {
              return this.errorMessage = false;
            }, 2000)
          });
        }
    },
  }
</script>

