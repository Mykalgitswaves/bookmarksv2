import { ref } from 'vue';

// This looks at a function and determines whether a user clicked inside of the ref element. Called only when element exists.
function clickedInsideElement(
    clientX, clientY, xStartingPoint,
    xEndingPoint, yStartingPoint, yBottomPoint,
) {
    if(clientX >= xStartingPoint && clientX <= xEndingPoint && clientY >= yStartingPoint && clientY <= yBottomPoint){
        return true
    } else {
        return false
    }
}

let clickedInsideMenu;
let clickedInsideMenuButton;

// hopefully this makes this more performant.
const menuDimensionCache = {};
const buttonDimensionCache = {};

// Uses a ref to handle the reactivity.
export const isMobileMenuShowing = ref(false);

export function autoCloseElementWithRef(refArray){
    // if client clicks outside the width and height of a 
    // Specific element then change the second argument to false.
    // We need to know the space the element in question takes up inside the document
    // So if the click event target is greater than the left x and less than the right x (calculated by adding element width to left x?), and less than the height, and greater than the height + the top y point (bottom of element) we can deduce the client clicked inside of the element.
    document.addEventListener('click', (e) => { 
            const menu = refArray[0];
            const button = refArray[1];
            // const menuWidth = menu.clientWidth;
            // const menuYStartingPoint = menuWidth.offsetTop;
            // const menuXStartingPoint = menuWidth.offsetLeft;
            // const menuYBottomPoint = menuYStartingPoint + menu.clientHeight
            // const menuXEndingPoint = menuXStartingPoint + width;

            // Use a cache to store dimensions of the menu after your initial click
            if (isMobileMenuShowing.value) {
                menuDimensionCache.width = menuDimensionCache.width ? menuDimensionCache.width : menu.clientWidth;
                menuDimensionCache.yStartingPoint = menuDimensionCache.yStartingPoint ? menuDimensionCache.yStartingPoint : menu.offsetTop;
                menuDimensionCache.xStartingPoint = menuDimensionCache.xStartingPoint ? menuDimensionCache.xStartingPoint : menu.offsetLeft;
                menuDimensionCache.yBottomPoint =  menuDimensionCache.yBottomPoint ? menuDimensionCache.yBottomPoint : menu.offsetTop + menu.clientHeight;
                menuDimensionCache.xEndingPoint = menuDimensionCache.xEndingPoint ? menuDimensionCache.xEndingPoint : menu.offsetLeft + menu.width;
            }

            buttonDimensionCache.width = buttonDimensionCache.width ? buttonDimensionCache.width : button.clientWidth;
            buttonDimensionCache.yStartingPoint = buttonDimensionCache.yStartingPoint ? buttonDimensionCache.yStartingPoint : button.offsetTop;
            buttonDimensionCache.xStartingPoint = buttonDimensionCache.xStartingPoint ? buttonDimensionCache.xStartingPoint : button.offsetLeft;
            
            buttonDimensionCache.yBottomPoint = buttonDimensionCache.yBottomPoint ? 
                buttonDimensionCache.yBottomPoint : 
                button.offsetTop + button.clientHeight;

            buttonDimensionCache.xEndingPoint = buttonDimensionCache.xEndingPoint ? 
                buttonDimensionCache.xEndingPoint :
                button.offsetLeft + button.clientWidth;

            let clientX = e.clientX;
            let clientY = e.clientY;
            
            clickedInsideMenu = clickedInsideElement(
                clientX, clientY, 
                menuDimensionCache.xStartingPoint,
                menuDimensionCache.xEndingPoint,
                menuDimensionCache.yStartingPoint,
                menuDimensionCache.yBottomPoint
            );

            clickedInsideMenuButton = clickedInsideElement(
                clientX, clientY, 
                buttonDimensionCache.xStartingPoint,
                buttonDimensionCache.xEndingPoint,
                buttonDimensionCache.yStartingPoint,
                buttonDimensionCache.yBottomPoint,
            )
        
        if (isMobileMenuShowing.value && clickedInsideMenuButton) {
            isMobileMenuShowing.value = true;
            return;
        }

        if (isMobileMenuShowing.value && !clickedInsideMenu || clickedInsideMenuButton) {
            isMobileMenuShowing.value = false;
            return;
        }
    });
}