import {app_router} from '../main.js'
const token = document.cookie;

export const finalizeUserController = {
  decorateUser: async function (object) {
    // #NOTE: Make sure you pass in a non proxy object using the toRaw Vue function.
    await fetch('http://127.0.0.1:8000/put-decorate-reader-preferences/', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(object)
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Network response was not ok')
        }
        return response.json()
      })
      .then((data) => {
        app_router.push(`/feed/${data.user_id}`)
      })
      .catch((error) => {
        // Handle any errors
        console.error('Error:', error)
        throw error
      })
  }
}
