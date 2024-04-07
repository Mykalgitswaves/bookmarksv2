<template>
    <div class="collaborator">
        <!-- We need to replace this with actual profile images -->
        <svg class="extra small-profile-image" xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:svgjs="http://svgjs.dev/svgjs" viewBox="0 0 700 700" width="50" ><defs><linearGradient gradientTransform="rotate(183, 0.5, 0.5)" x1="50%" y1="0%" x2="50%" y2="100%" id="ffflux-gradient"><stop stop-color="hsl(267, 172%, 20%)" stop-opacity="1" offset="0%"></stop><stop stop-color="hsl(100, 100%, 80%)" stop-opacity="1" offset="100%"></stop></linearGradient><filter id="ffflux-filter" x="-20%" y="-20%" width="140%" height="140%" filterUnits="objectBoundingBox" primitiveUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
            <feTurbulence type="fractalNoise" baseFrequency="0.005 0.003" numOctaves="1" seed="196" stitchTiles="stitch" x="0%" y="0%" width="100%" height="100%" result="turbulence"></feTurbulence>

            <feGaussianBlur stdDeviation="20 0" x="0%" y="0%" width="100%" height="100%" in="turbulence" edgeMode="duplicate" result="blur"></feGaussianBlur>

            <feBlend mode="color-dodge" x="0%" y="0%" width="100%" height="100%" in="SourceGraphic" in2="blur" result="blend"></feBlend>

            </filter></defs><rect width="100%" height="100%" fill="url(#ffflux-gradient)" filter="url(#ffflux-filter)"></rect>
        </svg>

        <div>
            <h4 class="collaborator-username">michael</h4>
            <p id="role" class="collaborator-role">role: creator</p>  
        </div>

        <button type="button"
            class="btn btn-danger"
        >
            remove
        </button>
    </div>
</template>
<style scoped>
    .collaborator {
        margin-left: auto;
        margin-right: auto;
        padding-top: var(--padding-sm);
        padding-bottom: var(--padding-sm);
        display: flex;
        align-items: center;
        justify-content: space-between;
        max-width: 640px;
        min-width: 280px;
        text-align: start;
        column-gap: 12px;
    }

    .collaborator-text {
        align-self: start;
    }

    .collaborator-username {
        font-size: var(--font-lg);
        font-weight: 500;
        color: var(--stone-800);
    }

    .btn-danger {
        background-color: var(--red-100);
        color: var(--red-700);
        border-radius: var(--radius-sm);
        padding-left: 12px;
        padding-right: 12px;
        margin-left: auto;
    }
</style>