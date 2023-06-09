export const createUserController = {
  createUser: async function (object) {
    // #NOTE: Make sure you pass in a non proxy object using the toRaw Vue function.
    await fetch('http://127.0.0.1:8000/post-create-reader/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
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
        // Handle the response data
        console.log('POST request successful:', data)
        return data
      })
      .catch((error) => {
        // Handle any errors
        console.error('Error:', error)
        throw error
      })
  },
  decodeToken: function(token) {
    // Implement your token decoding logic here
    // Replace the logic below with your actual token decoding logic
    // For example, if you're using JWT, you can use a library like `jsonwebtoken` to decode the token
    try {
      // #TODO: Replacewith other way to decode
      const decoded = jwt.verify(token, import.meta.env.MY_SECRET_KEY);
      return decoded;
    } catch (error) {
      console.error('Error decoding token:', error);
      return null;
    }
  },
  extractIdFromToken: function(token) {
    // Perform the necessary extraction logic specific to your token structure
    // For example, if your token is a JWT, you can decode it and extract the ID
    // Replace the logic below with your actual extraction logic
    const decodedToken = this.decodeToken(token);
    if (decodedToken) {
      return decodedToken.id;
    }
    return null;
  },
  getSessionTokenId: function() {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.startsWith('session_token=')) {
        const token = cookie.split('=')[1];
        // Extract the ID from the token
        const id = this.extractIdFromToken(token);
        return id;
      }
    }
    return null;
  },
  
}
