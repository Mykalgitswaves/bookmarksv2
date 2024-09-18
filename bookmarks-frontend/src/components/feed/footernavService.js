import { router } from '../../router/index';
import { navRoutes } from '../../services/urls';

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

export function goToBookClubsPage(user) {
    router.push(navRoutes.toBookClubsPage(user));
}

export const FooterViews = {
    default: 'default',
    bookclubs: 'bookclubs'
}