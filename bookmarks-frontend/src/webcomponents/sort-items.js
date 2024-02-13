import { html, LitElement, css } from 'lit';

export class SortItem extends LitElement {
    static instances = [];
    
    constructor(order, name, bookTitle, author, imgUrl) {
        super();
        this.order = order;
        this.name = name;
        this.bookTitle = bookTitle;
        this.author = author;
        this.imgUrl = imgUrl;
        this.draggedElement = SortItem.instances.find((i) => i.name = this.name);

        this.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData("order", this.order);
            e.dataTransfer.setData("name", this.name);
        });

        this.addEventListener('dragover', (e) => {
            e.preventDefault();
            //  Only add it once dude
            if (!e.target.renderRoot.children[0].classList.contains('dragged-over')) {
                e.target.renderRoot.children[0].classList.add('dragged-over')
            }
        });

        this.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.target.renderRoot.children[0].classList.remove('dragged-over')
        });

        this.addEventListener('drop', (e) => {
            e.preventDefault();
            
            e.target.renderRoot.children[0].classList.remove('dragged-over')
            let draggedFromIndex = parseInt(e.dataTransfer.getData("order"), 10);
            let draggedToIndex = parseInt(e.currentTarget.order, 10);
            
            
            if (draggedFromIndex < draggedToIndex) {
                e.currentTarget.parentNode.insertBefore(SortItem.instances[draggedFromIndex], e.currentTarget.nextSibling);
                // be able to insert before the end of a list
            } else {
                e.currentTarget.parentNode.insertBefore(SortItem.instances[draggedFromIndex], e.currentTarget);
            }
            // Thing being dropped on is e.target.order;
            // This is element being dragged;
            let newDraggedToOrder = parseInt(e.dataTransfer.getData("order"), 10);
            let draggedElement = this;
            let elementBeingDroppedOn = SortItem.instances[newDraggedToOrder];
            elementBeingDroppedOn.order = draggedElement.order;
        });
        SortItem.instances.push(this)
    }
  
    static get styles() {
        return css`
        :host {
            --spacing-sm: 14px;
            --spacing-xsm: 8px;
            --padding-md: var(--spacing-md);
            --radius-sm: 8px;
            --font-lg: 1.125rem;
            --font-sm: 0.875rem;
            --font-base: 1rem;
            --stone-100: #f5f5f4;
            --stone-500: #737373;
            --indigo-300: #a5b4fc;
            --indigo-600: #4f46e5;
        }

        .bs-b--book {
            display: grid;
            padding: var(--padding-xsm);
            border-radius: var(--radius-sm);
            grid-template-columns: 40px 40px auto 40px;
            align-items: center;
            column-gap: 8px;
            transition: all 250ms ease;
            cursor: grab;
            
            &:hover {
                background-color: var(--stone-100);
            }
            &.dragging {
                border-top: 8px solid var(--indigo-600);
            }
            &.dragged-over {
                border: 2px dotted var(--indigo-600);
            }
        }   
    
        .bs-b--book .sort {
            text-align: center;
            font-size: var(--font-lg);
            color: var(--stone-500);
            font-weight: 300;
        }
    
        .bs-b--book img {
            border-radius: var(--radius-sm);
            justify-self: center;
            
            width: 100%;
            height: 48px;
            object-fit: cover;
        }
        .bs-b--book .meta {
            padding-left: var(--padding-sm);
            .title { 
                color: var(--stone-800);
                font-size: var(--font-lg);
            }
            .author {
                color: var(--stone-500);
                font-size: var(--font-sm);
            }
        }
        `;
    }
    

    render() {
        return html`
        <div class="bs-b--book" draggable="true">
            <div class="sort">
                ${ this.order }
            </div>

            <img class="img" src="${this.imgUrl}" alt="">

            <div class="meta">
            <p class="title">${ this.bookTitle }</p>
            <p class="author">${ this.author }</p>
            </div>

            <div id="dragger">  
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path d="M9 13a1 1 0 1 1 0-2 1 1 0 0 1 0 2Zm7-1a1 1 0 1 1-2 0 1 1 0 0 1 2 0ZM9 8a1 1 0 1 1 0-2 1 1 0 0 1 0 2Zm7-1a1 1 0 1 1-2 0 1 1 0 0 1 2 0ZM9 18a1 1 0 1 1 0-2 1 1 0 0 1 0 2Zm6 0a1 1 0 1 1 0-2 1 1 0 0 1 0 2Z"></path></svg>
            </div>
        </div>
        `;
    }
}