

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
import HotTake from './icons/HotTake.vue';
import DefinitelyDidntReadIt from './icons/DefinitelyDidntReadIt.vue';
import StrangeHillToDieOn from './icons/StrangeHillToDieOn.vue';
import Facts from './icons/Facts.vue';
import NiceGippity from './icons/NiceGippity.vue';
import Hundred from './icons/Hundred.vue';
import Doubt from './icons/Doubt.vue';

export const ClubAwardsSvgMap = {
    dunce_cap: () => DunceCap,
    hot_take: () => HotTake,
    nice_gippity: () => NiceGippity,
    facts: () => Facts,
    strange_hill_to_die_on: () => StrangeHillToDieOn,
    definitely_didnt_read_it: () => DefinitelyDidntReadIt,
    '100': () => Hundred,
    doubt: () => Doubt,
} 