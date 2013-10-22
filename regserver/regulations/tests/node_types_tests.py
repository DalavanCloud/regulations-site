#vim: set encoding=utf-8
from unittest import TestCase

from regulations.generator.node_types import *


class NodeTypesTest(TestCase):
    def test_change_appendix(self):
        node_parts_before = ['243', 'A', '30(a)']
        node_parts_after = to_markup_id(node_parts_before)
        node_string = "-".join(node_parts_after)

        self.assertEqual('243-A-30a', node_string)

    def test_from_label(self):
        self.assertEqual(REGTEXT, from_label(['250', '5', 'A']))
        self.assertEqual(APPENDIX, from_label(['250', 'A']))
        self.assertEqual(APPENDIX, from_label(['250', 'A', '3(b)']))
        self.assertEqual(REGTEXT, from_label(['250']))
        self.assertEqual(REGTEXT, from_label(['250', '5']))
        self.assertEqual(REGTEXT, from_label(['250', '5', 'a', 'i', 'C']))
        self.assertEqual(EMPTYPART, from_label(['250', 'Subpart']))
        self.assertEqual(SUBPART, from_label(['250', 'Subpart', 'C']))
        self.assertEqual(INTERP, from_label(['250', 'Interp']))
        self.assertEqual(INTERP, from_label(['250', 'A', 'Interp']))
        self.assertEqual(INTERP, from_label(['250', '5', 'Interp']))
        self.assertEqual(INTERP, from_label(['250', '5', 'b', 'Interp']))
        self.assertEqual(INTERP, from_label(['250', '5', 'b', 'Interp', '1']))
        self.assertEqual(INTERP, from_label(['250', '5', 'Interp', '5', 'r']))

    def test_transform_part_none(self):
        part = '30'
        self.assertEqual('30', transform_part(part))

    def test_label_to_text(self):
        self.assertEqual('2323.4', label_to_text(['2323', '4']))
        self.assertEqual('2323.5(r)(3)',
                         label_to_text(['2323', '5', 'r', '3']))
        self.assertEqual('4', label_to_text(['2323', '4'], False))
        self.assertEqual('5(r)(3)',
                         label_to_text(['2323', '5', 'r', '3'], False))
        self.assertEqual(u'§ 2323.1',
                         label_to_text(['2323', '1'], True, True))
        self.assertEqual(u'§ 1', label_to_text(['2323', '1'], False, True))
        self.assertEqual('Appendix A', label_to_text(['2323', 'A']))
        self.assertEqual('Appendix A-4', label_to_text(['2323', 'A', '4']))
        self.assertEqual('Appendix A-4(b)(2)',
                         label_to_text(['2323', 'A', '4', 'b', '2']))
        self.assertEqual('Comment for 2323.5',
                         label_to_text(['2323', '5', 'Interp']))
        self.assertEqual('Comment for 2323.7(b)-1.v',
                         label_to_text(['2323', '7', 'b', 'Interp', '1', 'v']))
        self.assertEqual('Comment for Appendix Z',
                         label_to_text(['2323', 'Z', 'Interp']))
        self.assertEqual('Regulation 204', label_to_text(['204']))
        self.assertEqual('Supplement I to Part 204',
                         label_to_text(['204', 'Interp']))
