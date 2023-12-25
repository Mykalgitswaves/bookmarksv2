import { useRouter } from 'vue-router';

const router = useRouter();

export function goToSearchPage(user) {
    router.push(`/feed/${user}/search/`);
}

export function goToFeedPage(user) {
    router.push(`/feed/${user}/all`);
}

export function goToSocialPage(user) {
    router.push(`/feed/${user}/social/`)
}

export function goToUserPage(user) {
    router.push(`/feed/${user}`)
}