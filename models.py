# https://favtutor.com/blogs/doubly-linked-list-python
from fastapi import (
    HTTPException,
)

from database.db_helpers import User
import uuid

class Node:
    def __init__(self, data):
        self.item = data
        self.next = None
        self.prev = None
# Class for doubly Linked List
class DoublyLinkedList:
    def __init__(self):
        self.start_node = None
        self.size = int(0)
    # Insert element at the end
    def InsertToEnd(self, data):
        # Check if the list is empty
        new_node = Node(data)
        if self.start_node is None:
            self.start_node = new_node
            self.size += 1
            return
        n = self.start_node
        if n.item == new_node.item:
            raise HTTPException(400, 'Item already in list')
        # Iterate till the next reaches NULL
        while n.next is not None:
            n = n.next
            if n.item == new_node.item:
                raise HTTPException(400, 'Item already in list')
        n.next = new_node
        new_node.prev = n
        self.size += 1
    # Delete the element from data
    def DeleteNode(self, data):
        # Check if the List is empty
        if self.start_node is None:
            raise HTTPException(400, 'Item not in list')
        n = self.start_node
        if n.item == data:
            self.start_node = n.next
            self.start_node.prev = None
            self.size -= 1
            return
        while n.next is not None:
            n = n.next
            if n.item == data:
                n.prev.next = n.next
                if n.next:
                    n.next.prev = n.prev
                    self.size -= 1
                else:
                    pass # Case when tail --> Increase query simplicity
                return
        return HTTPException(400,'Item not in list')
        
    def reorder_node(self, node_data, prev_node_data, next_node_data):
        """
        Edge cases to consider:
            1)
                prev_node_data and next_node_data are not adjacent. This means we are trying to insert between to non adjacent nodes
            2)
                prev_node_data or next_node_data dont exist. This is ok in the instance that we are move to the head OR tail.
            3)
                node_data doesnt exist
        """
        if self.start_node is None:
            print("The list is empty")
            return

        # Find the node to be moved
        current = self.start_node
        while current and current.item != node_data:
            current = current.next

        if not current:
            print("Node to reorder not found")
            return

        # Detach the node from its current position
        if current.prev:
            current.prev.next = current.next
        else:
            self.start_node = current.next

        if current.next:
            current.next.prev = current.prev

        # Find the new previous and next nodes
        prev_node = None
        next_node = self.start_node

        if prev_node_data is not None:
            prev_node = self.start_node
            while prev_node and prev_node.item != prev_node_data:
                prev_node = prev_node.next

            if not prev_node:
                print("Previous node not found")
                return

            next_node = prev_node.next

        if next_node_data is not None:
            next_node = self.start_node
            while next_node and next_node.item != next_node_data:
                next_node = next_node.next

            if not next_node:
                print("Next node not found")
                return

            prev_node = next_node.prev

        # Place the node at the new position
        current.prev = prev_node
        current.next = next_node

        if prev_node:
            prev_node.next = current
        else:
            self.start_node = current

        if next_node:
            next_node.prev = current

    # Traversing and Displaying each element of the list
    def Display(self):
        if self.start_node is None:
            print("The list is empty")
            return
        else:
            n = self.start_node
            while n is not None:
                print("Element is: ", n.item)
                n = n.next
        print("\n")

    def to_array(self):
        items = []
        current = self.start_node
        while current:
            items.append(current)
            current = current.next
        return items
    
"""
    Bookshelves rely on a DoublyLinkedList implementation to handle logic. 
    data (a book) being sent to a bookshelf for an insertion should look like this:

        book = {
            order: int 
            name: str,
            book_title: str,
            author: [str],
            imgUrl: str
        }

    When we reorder we need to send references to previous nodes and next nodes and the current node we want to see?

    # TODO test that size actually works on DoublyLinkedList implementation.
    # TODO test that this shit is actually doable.
"""
class Bookshelf():
    def __init__(
        self, created_date: str, created_by: str, title: str, description: str,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.image_url: str
        self.books = DoublyLinkedList
        self.followers = set() # list of str's id.
        self.authors = set() # list of str's id.

        def add_book_to_shelf(self, data):
            book = Node(data=data)
            self.books.insert_to_end(book)
            
        def reorder_book(self, node_data, previous_node_data, next_node_data):
            if previous_node_data and next_node_data:
                self.books.reorder_node(node_data, previous_node_data, next_node_data)
            else:
                self.books.insert_to_end(node_data)
        
        def get_books(self):
            return self.books.to_array()
        
        def add_follower(self, user_id):
            self.followers.add(user_id)
        
        def add_author(self, user_id):
            # can only be 5 authors
            if len(self.authors) > 5:
                raise("400", "Bookshelves have a maximum of 5 authors")
            else:
                self.authors.add(user_id)

        def remove_author(self, user_id):
            self.authors.discard(user_id)


# TODO Add tests for Bookshelves either here or in a seperate file.