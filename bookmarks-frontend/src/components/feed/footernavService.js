import { router } from '../../router/index';

export function goToSearchPage(user) {
    router.push(`/feed/${user}/search`);
}

export function goToFeedPage(user) {
    router.push(`/feed/${user}/all`);
}

export function goToSocialPage(user) {
    router.push(`/feed/${user}/social`)
}

export function goToUserPage(user) {
    router.push(`/feed/${user}/user/${user}`)
}

export function goToBookshelvesPage(user) {
    router.push(`/feed/${user}/bookshelves/all`);
}

export function goToBookshelfPage(user, bookshelf_id) {
    router.push(`/feed/${user}/bookshelves/${bookshelf_id}`);
}