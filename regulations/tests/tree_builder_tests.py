from unittest import TestCase
from regulations.generator.layers import tree_builder
from regulations.generator.node_types import REGTEXT

import itertools


class TreeBuilderTest(TestCase):

    def build_tree(self):
        child = {
            'text': 'child text',
            'children': [],
            'label_id': '204-3',
            'label': ['204', '3'],
            'node_type': REGTEXT
        }
        tree = {
            'text': 'parent text',
            'children': [child],
            'label_id': '204',
            'label': ['204'],
            'node_type': REGTEXT
        }
        return tree

    def test_parent_in_tree(self):
        tree = self.build_tree()
        tree_hash = tree_builder.build_tree_hash(tree)
        self.assertEqual(tree_hash.keys(), ['204-3', '204'])

        self.assertTrue(tree_builder.parent_in_tree('204-3', tree_hash))

    def test_add_node(self):
        new_node = {
            'text': 'new node text',
            'children': [],
            'label_id': '204-4',
            'label': ['204', '4'],
            'node_type': REGTEXT
        }
        tree = self.build_tree()
        tree_hash = tree_builder.build_tree_hash(tree)
        self.assertEqual(tree_hash.keys(), ['204-3', '204'])

        self.assertEqual(len(tree_hash['204']['children']), 1)
        tree_builder.add_node_to_tree(new_node, '204', tree_hash)
        self.assertEqual(len(tree_hash['204']['children']), 2)

        child_labels = [c['label_id'] for c in tree_hash['204']['children']]
        self.assertEqual(child_labels, ['204-3', '204-4'])

    def test_make_label_sortable_roman(self):
        label = "iv"
        sortable = tree_builder.make_label_sortable(label, roman=True)
        self.assertEquals(sortable, 4)

    def test_make_label_sortable_not_roman(self):
        label = "iv"
        sortable = tree_builder.make_label_sortable(label)
        self.assertEquals(sortable, ('iv',))

    def test_parent_label(self):
        node = {'node_type': 'REGTEXT', 'label': ['204', 'a', '1', 'ii']}
        parent_label = tree_builder.parent_label(node)
        self.assertEquals(['204', 'a', '1'], parent_label)

        node = {'node_type': 'INTERP', 'label': ['204', 'Interp']}
        parent_label = tree_builder.parent_label(node)
        self.assertEquals(['204'], parent_label)

        node = {'node_type': 'INTERP', 'label': ['204', '2', 'Interp']}
        parent_label = tree_builder.parent_label(node)
        self.assertEquals(['204', 'Interp'], parent_label)

        node = {'node_type': 'INTERP', 'label': ['204', '2', 'a', 'Interp']}
        parent_label = tree_builder.parent_label(node)
        self.assertEquals(['204', '2', 'Interp'], parent_label)

        node = {'node_type': 'INTERP',
                'label': ['204', '2', 'Interp', '1']}
        parent_label = tree_builder.parent_label(node)
        self.assertEquals(['204', '2', 'Interp'], parent_label)

        node = {'node_type': 'INTERP',
                'label': ['204', '2', 'Interp', '1', 'i']}
        parent_label = tree_builder.parent_label(node)
        self.assertEquals(['204', '2', 'Interp', '1'], parent_label)

    def test_roman_nums(self):
        first_five = list(itertools.islice(tree_builder.roman_nums(), 0, 5))
        self.assertEquals(['i', 'ii', 'iii', 'iv', 'v'], first_five)

    def test_add_child(self):
        tree = self.build_tree()

        child = {
            'children': [],
            'label': ['204', '2'],
            'label_id': '204-2',
            'node_type': REGTEXT,
            'sortable': (2,),
            'text': 'child text',
        }

        static_child = {
            'children': [],
            'label': ['204', '3'],
            'label_id': '204-3',
            'node_type': REGTEXT,
            'sortable': (3,),
            'text': 'child text',
        }

        static_tree = {
            'children': [child, static_child],
            'text': 'parent text',
            'label': ['204'],
            'label_id': '204',
            'node_type': REGTEXT
        }

        tree_builder.add_child(tree, child)
        self.assertEquals(static_tree, tree)

    def test_add_child_appendix(self):
        parent = {'children': [
            {'node_type': 'APPENDIX', 'label': ['204', 'A', '1']},
            {'node_type': 'APPENDIX', 'label': ['204', 'A', '3']},
            ]}

        child_to_add = {'node_type': 'APPENDIX', 'label': ['204', 'A', '2(a)']}
        tree_builder.add_child(parent, child_to_add)
        self.assertEquals(
            ['204-A-1', '204-A-2(a)', '204-A-3'],
            ['-'.join(c['label']) for c in parent['children']]
            )

    def test_add_child_interp(self):
        parent = {'children': [
            {'node_type': 'INTERP', 'label': ['204', '4', 'Interp']},
            {'node_type': 'INTERP', 'label': ['204', '2', 'Interp']}
        ]}
        tree_builder.add_child(parent, {'node_type': 'INTERP',
                                        'label': ['204', '3', 'Interp']})
        self.assertEqual([(2,), (3,), (4,)],
                         [c['sortable'] for c in parent['children']])

        prefix = ['204', '4', 'a', '2']
        parent = {'children': [
            {'node_type': 'INTERP', 'label': prefix + ['v', 'Interp']},
            {'node_type': 'INTERP', 'label': prefix + ['iv', 'Interp']}
        ]}
        tree_builder.add_child(parent, {'node_type': 'INTERP',
                                        'label': prefix + ['ix', 'Interp']})
        self.assertEqual([4, 5, 9],
                         [c['sortable'] for c in parent['children']])

        prefix = ['204', '4', 'Interp']
        parent = {'children': [
            {'node_type': 'INTERP', 'label': prefix + ['1']},
            {'node_type': 'INTERP', 'label': prefix + ['3']}
        ]}
        tree_builder.add_child(parent, {'node_type': 'INTERP',
                                        'label': prefix + ['2']})
        self.assertEqual([(1,), (2,), (3,)],
                         [c['sortable'] for c in parent['children']])

        prefix = ['204', 'Interp', '2']
        parent = {'children': [
            {'node_type': 'INTERP', 'label': prefix + ['v']},
            {'node_type': 'INTERP', 'label': prefix + ['iv']}
        ]}
        tree_builder.add_child(parent, {'node_type': 'INTERP',
                                        'label': prefix + ['ix']})
        self.assertEqual([4, 5, 9],
                         [c['sortable'] for c in parent['children']])
