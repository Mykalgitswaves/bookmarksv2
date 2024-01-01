# https://favtutor.com/blogs/doubly-linked-list-python

class Node:
    def __init__(self, data):
        self.item = data
        self.next = None
        self.prev = None
# Class for doubly Linked List
class DoublyLinkedList:
    def __init__(self):
        self.start_node = None
    # Insert Element to Empty list
    def InsertToEmptyList(self, data):
        if self.start_node is None:
            new_node = Node(data)
            self.start_node = new_node
        else:
            print("The list is empty")
    # Insert element at the end
    def InsertToEnd(self, data):
        # Check if the list is empty
        if self.start_node is None:
            new_node = Node(data)
            self.start_node = new_node
            return
        n = self.start_node
        # Iterate till the next reaches NULL
        while n.next is not None:
            n = n.next
        new_node = Node(data)
        n.next = new_node
        new_node.prev = n
    # Delete the elements from the start
    def DeleteAtStart(self):
        if self.start_node is None:
            print("The Linked list is empty, no element to delete")
            return 
        if self.start_node.next is None:
            self.start_node = None
            return
        self.start_node = self.start_node.next
        self.start_prev = None;
    # Delete the elements from the end
    def delete_at_end(self):
        # Check if the List is empty
        if self.start_node is None:
            print("The Linked list is empty, no element to delete")
            return 
        if self.start_node.next is None:
            self.start_node = None
            return
        n = self.start_node
        while n.next is not None:
            n = n.next
        n.prev.next = None
    def reorder_node(self, node_data, prev_node_data, next_node_data):
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

    