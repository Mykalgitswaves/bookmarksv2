const baseUrl = 'http://127.0.0.1:8000/'

export const urls = {
    // Note there is an extra slash after base so dont start paths with slash
    baseUrl: baseUrl,
    setup: {
        name: baseUrl + 'setup-reader/name',
        bookByText: (text) => (`${baseUrl}books/${text}`),
    },
    authUrl: baseUrl + 'api/auth_user/',
    booksByN: baseUrl + 'books/n/',
    login: baseUrl + 'api/login/',
    author: baseUrl + 'api/author/',
}