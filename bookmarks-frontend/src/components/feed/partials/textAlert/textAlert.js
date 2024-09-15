import IconWarning from './icons/IconWarning.vue';
import IconInfo from './icons/IconInfo.vue';
import IconError from './icons/IconError.vue';

export const TEXT_ALERT = {
    default: 'warning',
    variants: [
        'info', 'warning', 'error' 
    ],
    info: {
        cls: 'info',
        icon: IconInfo,
    },
    warning: {
        cls: 'warning',
        icon: IconWarning,
    }, 
    error: {
        cls: 'error',
        icon: () => {}
    }
}