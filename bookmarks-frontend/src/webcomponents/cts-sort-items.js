import { html, LitElement, css } from 'lit';

export class CTSSortItem extends LitElement {
    static instances = [];
    static isSwapping = false;
    static currentSwapIndex = -1;

    constructor(index, name, bookTitle, author, imgUrl) {
        super();
        this.index = index;
        this.name = name;
        this.bookTitle = bookTitle;
        this.author = author;
        this.imgUrl = imgUrl;
        this.draggedElement = CTSSortItem.instances.find((i) => i.name === this.name);

        CTSSortItem.instances.push(this);
    }

    static get properties() {
        return {
            isSwapping: { type: Boolean }
        };
    }

    static toggleSwap() {
        debugger;
        CTSSortItem.isSwapping = !CTSSortItem.isSwapping;
        CTSSortItem.currentSwapIndex = CTSSortItem.isSwapping ? CTSSortItem.instances.findIndex(instance => instance === this) : -1;
    }

    renderInsertTarget(isPrevious) {
        const index = isPrevious ? CTSSortItem.currentSwapIndex : CTSSortItem.currentSwapIndex + 1;
        const adjacentElement = CTSSortItem.instances[index];
        if (adjacentElement && CTSSortItem.isSwapping) {
            return html`
                <label for="${adjacentElement.id}">
                    <span>Insert here</span>
                    <input id="${adjacentElement.id}" type="checkbox"/>
                </label>`;
        } else {
            return html``;
        }
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
        
        .bs-b-book-input {
            border: 1px solid var(--stone-100);
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
        ${this.renderInsertTarget(true)}

        <label class="bs-b" for="${this.id}">   

            <div class="bs-b--book">
                <div class="sort">
                    ${ this.order }
                </div>

                <img class="img" src="${this.imgUrl}" alt="">

                <div class="meta">
                <p class="title">${ this.bookTitle }</p>
                <p class="author">${ this.author }</p>
                </div>

                <div id="dragger">  
                <input id="${this.id}" type="checkbox" class="bs-b-book-input" @click=${CTSSortItem.toggleSwap}/>
                </div>
            </div>
        </label>

        ${this.renderInsertTarget(false)}
        `;
    }
}