

export const Award = {
    cls: 'award',

    statuses: {
        // Designates an award that can still be granted.
        grantable: 'grantable',
        // Mid request used to prevent sending redundant promises.
        loading: 'loading',
        // Designates an award that can no longer be granted. 
        expired: 'expired',
    },

    // Property used to manipulate the dom.
    status: ''
}


import DunceCap from './icons/DunceCap.vue';

export const ClubAwardsSvgMap = {
    'dunce-cap': () => DunceCap 
}