from unittest import TestCase
from django.test import RequestFactory

from regulations.views.diff import *


class ChromeSectionDiffViewTests(TestCase):
    def test_diff_toc(self):
        """Integration test."""
        old_toc = [{'section_id': '8888-1', 'index': ['8888', '1']},
                   {'section_id': '8888-3', 'index': ['8888', '3']},
                   {'section_id': '8888-4', 'index': ['8888', '4']},
                   {'section_id': '8888-A', 'index': ['8888', 'A']},
                   {'section_id': '8888-B', 'index': ['8888', 'B']},
                   {'section_id': '8888-Interp', 'index': ['8888', 'Interp']}]
        diff = {
            '8888-2': {'op': 'added',
                       'node': {'title': '8888.2', 'label': ['8888', '2']}},
            '8888-C': {'op': 'added',
                       'node': {'title': 'App C', 'label': ['8888', 'C']}},
            '8888-1-a': {'op': 'modified'},
            '8888-B': {'op': 'deleted'},
            '8888-3-b': {'op': 'deleted'},
            '8888-B-1': {'op': 'modified'}
        }

        result = diff_toc('oldold', 'newnew', old_toc, diff, 'from_ver')
        self.assertEqual(8, len(result))
        self.assertTrue('8888-1' in result[0]['url'])
        self.assertTrue('?from_version=from_ver' in result[0]['url'])
        self.assertEqual('8888-1', result[0]['section_id'])
        self.assertEqual('modified', result[0]['op'])
        self.assertTrue('8888-2' in result[1]['url'])
        self.assertTrue('?from_version=from_ver' in result[1]['url'])
        self.assertEqual('8888-2', result[1]['section_id'])
        self.assertEqual('added', result[1]['op'])
        self.assertTrue('8888-3' in result[2]['url'])
        self.assertTrue('?from_version=from_ver' in result[2]['url'])
        self.assertEqual('8888-3', result[2]['section_id'])
        self.assertEqual('modified', result[2]['op'])
        self.assertTrue('8888-4' in result[3]['url'])
        self.assertTrue('?from_version=from_ver' in result[3]['url'])
        self.assertEqual('8888-4', result[3]['section_id'])
        self.assertFalse('op' in result[3])
        self.assertTrue('8888-A' in result[4]['url'])
        self.assertTrue('?from_version=from_ver' in result[4]['url'])
        self.assertEqual('8888-A', result[4]['section_id'])
        self.assertFalse('op' in result[4])
        self.assertTrue('8888-B' in result[5]['url'])
        self.assertTrue('?from_version=from_ver' in result[5]['url'])
        self.assertEqual('8888-B', result[5]['section_id'])
        self.assertEqual('deleted', result[5]['op'])
        self.assertTrue('8888-C' in result[6]['url'])
        self.assertTrue('?from_version=from_ver' in result[6]['url'])
        self.assertEqual('8888-C', result[6]['section_id'])
        self.assertEqual('added', result[6]['op'])
        self.assertTrue('8888-Interp' in result[7]['url'])
        self.assertEqual('8888-Interp', result[7]['section_id'])
        self.assertFalse('op' in result[7])
        for el in result:
            self.assertTrue('oldold', el['url'])
            self.assertTrue('newnew', el['url'])

    def test_interp_headers(self):
        from django.template import loader, Context
        t = loader.get_template('interp-tree.html')
        context_dict = {'interp': {
            'header': '<ins>My header</ins>', 'section_header': True}}
        response = t.render(Context(context_dict))
        tags_preserved_header = '<h3 tabindex=\"0\"> <ins>My header</ins></h3>'
        self.assertTrue(tags_preserved_header in response)

    def test_add_main_content(self):
        context = {
            'main_content_context': {'newer_version': '1', 'TOC': 'toc'},
            'label_id': '111-222',
            'version': '2'}
        request = RequestFactory().get('?new_version=1')
        csdv = ChromeSectionDiffView()
        csdv.request = request
        csdv.add_diff_content(context)
        self.assertEqual(context['from_version'], '2')
        self.assertEqual(context['left_version'], '2')
        self.assertEqual(context['right_version'], '1')
        self.assertEqual(context['TOC'], 'toc')


class PartialSectionDiffViewTests(TestCase):
    def test_footer_nav(self):
        view = PartialSectionDiffView()
        toc = [{'section_id': '9898-1'}, {'section_id': '9898-5'},
               {'section_id': '9898-A'}, {'section_id': '9898-Interp'}]
        self.assertEqual({}, view.footer_nav(
            '9898-2', toc, 'old', 'new', 'from'))

        result = view.footer_nav('9898-1', toc, 'old', 'new', 'from')
        self.assertFalse('previous' in result)
        self.assertTrue('9898-5' in result['next']['url'])
        self.assertTrue('old' in result['next']['url'])
        self.assertTrue('new' in result['next']['url'])
        self.assertTrue('?from_version=from' in result['next']['url'])

        result = view.footer_nav('9898-5', toc, 'old', 'new', 'from')
        self.assertTrue('9898-1' in result['previous']['url'])
        self.assertTrue('old' in result['previous']['url'])
        self.assertTrue('new' in result['previous']['url'])
        self.assertTrue('?from_version=from' in result['previous']['url'])
        self.assertTrue('9898-A' in result['next']['url'])
        self.assertTrue('old' in result['next']['url'])
        self.assertTrue('new' in result['next']['url'])
        self.assertTrue('?from_version=from' in result['next']['url'])

        result = view.footer_nav('9898-A', toc, 'old', 'new', 'from')
        self.assertTrue('9898-5' in result['previous']['url'])
        self.assertTrue('old' in result['previous']['url'])
        self.assertTrue('new' in result['previous']['url'])
        self.assertTrue('?from_version=from' in result['previous']['url'])
        self.assertTrue('9898-Interp' in result['next']['url'])
        self.assertTrue('old' in result['next']['url'])
        self.assertTrue('new' in result['next']['url'])
        self.assertTrue('?from_version=from' in result['next']['url'])

        result = view.footer_nav('9898-Interp', toc, 'old', 'new', 'from')
        self.assertTrue('9898-A' in result['previous']['url'])
        self.assertTrue('old' in result['previous']['url'])
        self.assertTrue('new' in result['previous']['url'])
        self.assertTrue('?from_version=from' in result['previous']['url'])
        self.assertFalse('next' in result)
