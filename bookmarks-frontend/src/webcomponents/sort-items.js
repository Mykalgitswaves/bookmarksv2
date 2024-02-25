import { html, LitElement, css } from 'lit';

export class SortItem extends LitElement {
    static instances = [];
    static selectedInstances = [];
    
    constructor(order, id, bookTitle, author, imgUrl) {
        super();
        this.order = order;
        this._id = id;
        this.bookTitle = bookTitle;
        this.author = author;
        this.imgUrl = imgUrl;
        this.draggedElement = this;

        this.addEventListener('dragstart', this.onDragStart.bind(this));
        this.addEventListener('dragover', this.onDragOver.bind(this));
        this.addEventListener('dragleave', this.onDragLeave.bind(this));
        this.addEventListener('drop', this.onDrop.bind(this));
        SortItem.instances.push(this)
    }

    onDragStart(event) {
        event.dataTransfer.setData("order", this.order);
        event.dataTransfer.setData("id", this._id);
        this.scrollIntoView({ behavior: "smooth", block: "end", inline: "nearest" });
    }

    onDragOver(event) {
        event.preventDefault();
        if (!event.target.renderRoot.firstElementChild.classList.contains('dragged-over')) {
            event.target.renderRoot.firstElementChild.classList.add('dragged-over');
        }
    }

    onDragLeave(event) {
        event.preventDefault();
        event.target.renderRoot.firstElementChild.classList.remove('dragged-over');
    }

    onDrop(event) {
        event.preventDefault();
        event.target.renderRoot.firstElementChild.classList.remove('dragged-over');
        const draggedFromIndex = parseInt(event.dataTransfer.getData("order"), 10);
        const draggedToIndex = parseInt(this.order, 10);
 
        const reordered = new CustomEvent("reordered", {
            detail: { 
                book_id: SortItem.instances[draggedFromIndex],
                prev_book_id: SortItem.instances[draggedToIndex - 1],
                next_book_id: SortItem.instances[draggedToIndex],
            },
            bubbles: true,
        });

        event.target.dispatchEvent(reordered);
        const parent = event.currentTarget.parentNode;
        const insertBeforeElement = parent.children[draggedToIndex];

        if (draggedToIndex === SortItem.instances.length - 1) {
            // Dragging to end
            debugger;
            parent.appendChild(SortItem.instances[draggedFromIndex]);
        } else if (draggedToIndex === 0){
            debugger;
            // Dragging to beginning.
            parent.insertBefore(SortItem.instances[draggedFromIndex], SortItem.instances[0]);
        } else {
            debugger;
            parent.insertBefore(SortItem.instances[draggedFromIndex], insertBeforeElement);
        }
        
        // Update the order of all elements after the dragged element
        // SortItem.instances.forEach((item, index) => {
        //     if (index >= draggedFromIndex && index < draggedToIndex) {
        //         item.order = index + 1;
        //     } else if (index <= draggedFromIndex && index > draggedToIndex) {
        //         item.order = index - 1;
        //     }
        // });

        this.order = draggedToIndex;
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
                border-top: 2px dotted var(--indigo-600);
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

            <label for="select-${this._id}">  
                <input class="select" type="checkbox" id="select-${this._id}" value="${ this._id }"/>
            </label>
        </div>
        `;
    }
}