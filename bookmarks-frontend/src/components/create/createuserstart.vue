<template>
  <h1 class="text-center text-4xl font-medium mb-16">Create account</h1>

  <form
    class="grid grid-cols-1 w-80 h-80 gap-2 place-content-center"
    action="submitForm"
    method="POST"
  >
    <label class="gray-700">Enter your real name (or nickname)</label>
    <input
      class="py-2 px-4 rounded-md border-2 border-indigo-200"
      :v-model="formBlob.commonname"
      name="fullname"
      type="text"
      placeholder="Goffert"
    />
    <label class="gray-700">Enter your username (email)</label>
    <input
      class="py-2 px-4 rounded-md border-2 border-indigo-200"
      :v-model="formBlob.name"
      name="fullname"
      type="text"
      placeholder="Email"
    />

    <label class="gray-700">Password</label>
    <input
      class="py-2 px-4 rounded-md border-2 border-indigo-200"
      :v-model="formBlob.password"
      name="password"
      type="text"
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
      @click.prevent="submitForm"
    >
      Continue
    </button>
  </form>
</template>

<script>
export default {
  data() {
    return {
      formBlob: {}
    }
  }
}
</script>
