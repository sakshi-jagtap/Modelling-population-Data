"""Assignment 2: Trees for Treemap

=== CSC148 Fall 2020 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""

from __future__ import annotations
import os
from random import randint
import math

from typing import Tuple, List, Optional


class AbstractTree:
    """A tree that is compatible with the treemap visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this assignment will involve you adding and implementing
    new public *methods* for this interface.

    === Public Attributes ===
    data_size: the total size of all leaves of this tree.
    colour: The RGB colour value of the root of this tree.
        Note: only the colours of leaves will influence what the user sees.

    === Private Attributes ===
    _root: the root value of this tree, or None if this tree is empty.
    _subtrees: the subtrees of this tree.
    _parent_tree: the parent tree of this tree; i.e., the tree that contains
        this tree
        as a subtree, or None if this tree is not part of a larger tree.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.
    - colour's elements are in the range 0-255.

    - If _root is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.
    - _subtrees IS allowed to contain empty subtrees (this makes deletion
      a bit easier).

    - if _parent_tree is not empty, then self is in _parent_tree._subtrees
    """
    data_size: int
    colour: (int, int, int)
    _root: Optional[object]
    _subtrees: List[AbstractTree]
    _parent_tree: Optional[AbstractTree]

    def __init__(self: AbstractTree, root: Optional[object],
                 subtrees: List[AbstractTree], data_size: int = 0) -> None:
        """Initialize a new AbstractTree.

        If <subtrees> is empty, <data_size> is used to initialize this tree's
        data_size. Otherwise, the <data_size> parameter is ignored, and this
        tree's data_size is computed from the data_sizes of the subtrees.

        If <subtrees> is not empty, <data_size> should not be specified.

        This method sets the _parent_tree attribute for each subtree to self.

        A random colour is chosen for this tree.

        Precondition: if <root> is None, then <subtrees> is empty.
        """
        self._root = root
        self._subtrees = subtrees
        self._parent_tree = None

        # 1. Initialize self.colour and self.data_size,
        # according to the docstring.
        self.colour = (randint(0, 255), randint(0, 255), randint(0, 255))

        if not self._subtrees:
            self.data_size = data_size
        else:
            self.data_size = 0
            for subtree in subtrees:
                self.data_size += subtree.data_size

        # 2. Properly set all _parent_tree attributes in self._subtrees

        for tree in self._subtrees:
            tree._parent_tree = self

    def is_empty(self: AbstractTree) -> bool:
        """Return True if this tree is empty."""
        return self._root is None

    def generate_treemap(self: AbstractTree, rect: Tuple[int, int, int, int]) \
            -> List[Tuple[Tuple[int, int, int, int], Tuple[int, int, int]]]:
        """Run the treemap algorithm on this tree and return the rectangles.

        Each returned tuple contains a pygame rectangle and a colour:
        ((x, y, width, height), (r, g, b)).

        One tuple should be returned per non-empty leaf in this tree.

        @type self: AbstractTree
        @type rect: (int, int, int, int)
            Input is in the pygame format: (x, y, width, height)
        @rtype: list[((int, int, int, int), (int, int, int))]
        """

        # Read the handout carefully to help get started identifying base cases,
        # and the outline of a recursive step.
        #
        # Programming tip: use "tuple unpacking assignment" to easily extract
        # coordinates of a rectangle, as follows.

        if self.is_empty():
            return []
        if self.data_size == 0:
            return []
        if self._subtrees == [] and self.data_size > 0:
            return [(rect, self.colour)]

        leaves = []
        for leaf in self._subtrees:
            if not leaf.is_empty() and leaf.data_size != 0:
                leaves.append(leaf)

        last_leaf = len(leaves) - 1
        for leaf in range(last_leaf, -1):
            if leaves[leaf].is_empty() or leaves[leaf].data_size == 0:
                last_leaf = leaf
        last_rect = last_leaf

        lst = []
        x, y, width, height = rect
        if width <= height:
            remainder = 0
            for leaf, leave in enumerate(leaves):
                if leave.data_size > 0 and leaf != last_rect:
                    delta_y = int(math.floor((leave.data_size / self.
                                              data_size) * height))
                    lst += [leave.generate_treemap(
                        (x, y + remainder, width, delta_y))]
                    remainder += delta_y
                elif leaf == last_rect:
                    delta_y = height - remainder
                    lst += [leave.generate_treemap(
                        (x, y + remainder, width, delta_y))]
        else:
            remainder2 = 0
            for leaf, leave in enumerate(leaves):
                if leave.data_size > 0 and leaf != last_rect:
                    delta_x = int(math.floor((leave.data_size / self.
                                              data_size) * width))
                    lst += [leave.generate_treemap(
                        (x + remainder2, y, delta_x, height))]
                    remainder2 += delta_x
                elif leaf == last_rect:
                    delta_x = width - remainder2
                    lst += [leave.generate_treemap(
                        (x + remainder2, y, delta_x, height))]
        return unwind(lst)

    def update_data_size(self, factor: int) -> None:
        """
        assuming the data size has changed, update the data sizes for all parent
        trees above this Node

        """

        if self._parent_tree is None:
            self.data_size += factor
        else:
            self.data_size += factor
            self._parent_tree.update_data_size(factor)

    def leaves(self) -> List[AbstractTree]:
        """
        list all of the leaves in the tree
        """
        if not self._subtrees:
            return [self]
        lst = []
        for subtree in self._subtrees:
            lst.extend(subtree.leaves())
        return lst

    def get_separator(self: AbstractTree) -> str:
        """Return the string used to separate nodes in the string
        representation of a path from the tree root to a leaf.

        Used by the treemap visualiser to generate a string displaying
        the items from the root of the tree to the currently selected leaf.

        This should be overridden by each AbstractTree subclass, to customize
        how these items are separated for different data domains.
        """
        raise NotImplementedError


def unwind(nested_lst: List) -> \
        List[Tuple[Tuple[int, int, int, int], Tuple[int, int, int]]]:
    """
    Return a list from a nested list.
    """
    if not isinstance(nested_lst, list):
        return nested_lst
    lst = []
    for i, sublist in enumerate(nested_lst):
        if isinstance(sublist, list):
            lst += unwind(nested_lst[i])
        else:
            lst += [nested_lst[i]]
    return lst


class FileSystemTree(AbstractTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _root attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/David/csc148/assignments'

    The data_size attribute for regular files as simply the size of the file,
    as reported by os.path.getsize.
    """

    def __init__(self: FileSystemTree, path: str) -> None:
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.
        """
        # Remember that you should recursively go through the file system
        # and create new FileSystemTree objects for each file and folder
        # encountered.
        #
        # Also remember to make good use of the superclass constructor!

        if not os.path.isdir(path):
            root = os.path.basename(path)
            subtrees = []
            data_size = os.path.getsize(path)
            super().__init__(root, subtrees, data_size)
        else:
            root = os.path.basename(path)
            subtrees = []
            for folder in os.listdir(path):
                subtrees += [FileSystemTree(os.path.join(path, folder))]
            super().__init__(root, subtrees)

    def get_separator(self: AbstractTree) -> str:
        """Return the string used to separate nodes in the string
        representation of a path from the tree root to a leaf.
        """
        if not self._parent_tree:
            return str(self._root)
        return os.path.join(self._parent_tree.get_separator(), str(self._root))


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(
        config={
            'extra-imports': ['os', 'random', 'math'],
            'generated-members': 'pygame.*'})
