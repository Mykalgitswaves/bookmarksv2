export const fetchController = {
    // CAshMoneyCOokies
    generateCSRFToken: function() {
        // Generate a random string for the CSRF token
        const randomString = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
      
        // Set the CSRF token as a cookie
        document.cookie = `csrftoken=${randomString}; Path=/; Secure; SameSite=Lax`;
      
        return randomString;
      }
}

