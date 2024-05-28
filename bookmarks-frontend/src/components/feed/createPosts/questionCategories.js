import IconCharacter from '../../svg/icon-character.vue';
import IconPlot from '../../svg/icon-path.vue'; 
import IconConflict from '../../svg/icon-conflict.vue';
import IconTone from '../../svg/icon-tone.vue';
import IconCustomResponse from '../../svg/icon-custom-response.vue';
import IconSetting from '../../svg/icon-setting-category.vue';

export const categoryIconMapping = {
    // 'all': null,
    'character':  IconCharacter,
    'plot': IconPlot,
    'conflict': IconConflict,
    'resolution': null,
    'tone': IconTone,
    'custom': IconCustomResponse,
    'setting': IconSetting,
}