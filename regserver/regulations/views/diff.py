#vim: set encoding=utf-8

from regulations.generator import generator
from regulations.generator.html_builder import HTMLBuilder
from regulations.generator.layers.toc_applier import TableOfContentsLayer
from regulations.generator.node_types import EMPTYPART, REGTEXT
from regulations.generator.versions import fetch_grouped_history
from regulations.views import error_handling, utils
from regulations.views.chrome import ChromeView
from regulations.views.partial import PartialView

from django.core.urlresolvers import reverse


def get_appliers(label_id, older, newer):
    diff = generator.get_diff_applier(label_id, older, newer)

    if diff is None:
        raise error_handling.MissingContentException()

    appliers = utils.handle_diff_layers(
        'graphics,paragraph,keyterms,defined',
        label_id,
        older,
        newer)
    appliers += (diff,)
    return appliers


class PartialSectionDiffView(PartialView):
    """ A diff view of a partial section. """
    template_name = 'regulation-content.html'

    def get(self, request, *args, **kwargs):
        """ Override GET so that we can catch and propagate any errors. """

        try:
            return super(PartialSectionDiffView, self).get(request, *args,
                                                           **kwargs)
        except error_handling.MissingContentException, e:
            return error_handling.handle_generic_404(request)

    def get_context_data(self, **kwargs):
        # We don't want to run the content data of PartialView -- it assumes
        # we will be applying layers
        context = super(PartialView, self).get_context_data(**kwargs)

        label_id = context['label_id']
        older = context['version']
        newer = context['newer_version']

        tree = generator.get_tree_paragraph(label_id, older)

        if tree is None:
            #TODO We need a more complicated check here to see if the diffs
            #add the requested section. If not -> 404
            tree = {}

        appliers = get_appliers(label_id, older, newer)

        builder = HTMLBuilder(*appliers)
        builder.tree = tree
        builder.generate_html()

        child_of_root = builder.tree
        if builder.tree['node_type'] == REGTEXT:
            child_of_root = {
                'node_type': EMPTYPART,
                'children': [builder.tree]}
        context['tree'] = {'children': [child_of_root]}
        return context


class ChromeSectionDiffView(ChromeView):
    """Search results with chrome"""
    template_name = 'diff-chrome.html'
    partial_class = PartialSectionDiffView
    check_tree = False
    has_sidebar = False

    def add_main_content(self, context):
        super(ChromeSectionDiffView, self).add_main_content(context)
        context['left_version'] = context['version']
        context['right_version'] = \
            context['main_content_context']['newer_version']
        diff = generator.get_diff_json(
            context['reg_part'], context['version'], context['right_version'])

        old_toc = utils.table_of_contents(
            context['reg_part'],
            context['version'],
            self.partial_class.sectional_links)
        context['TOC'] = diff_toc(context, old_toc, diff)


def diff_toc(context, old_toc, diff):
    compiled_toc = list(old_toc)
    for node in (v['node'] for v in diff.values() if v['op'] == 'added'):
        if len(node['label']) == 2 and node['title']:
            element = {
                'label': node['title'],
                'index': node['label'],
                'section_id': '-'.join(node['label']),
                'op': 'added'
            }
            data = {'index': node['label'], 'title': node['title']}
            TableOfContentsLayer.section(element, data)
            TableOfContentsLayer.appendix_supplement(element, data)
            compiled_toc.append(element)

    modified, deleted = modified_deleted_sections(diff)
    for el in compiled_toc:
        newer_version = context['main_content_context']['newer_version']
        el['url'] = reverse('chrome_section_diff_view', kwargs={
            'label_id': el['section_id'], 'version': context['version'],
            'newer_version': newer_version})
        # Deleted first, lest deletions in paragraphs affect the section
        if tuple(el['index']) in deleted and 'op' not in el:
            el['op'] = 'deleted'
        if tuple(el['index']) in modified and 'op' not in el:
            el['op'] = 'modified'

    return sort_toc(compiled_toc)


def sort_toc(toc):
    def normalize(label):
        normalized = []
        for part in label:
            try:
                normalized.append(int(part))
            except ValueError:
                normalized.append(part)
        return normalized

    return sorted(toc, key=lambda el: tuple(normalize(el['index'])))


def modified_deleted_sections(diff):
    modified, deleted = set(), set()
    for label, diff_value in diff.iteritems():
        label = tuple(label.split('-'))
        if 'Interp' in label:
            section_label = (label[0], 'Interp')
        else:
            section_label = tuple(label[:2])

        # Whole section was deleted
        if diff_value['op'] == 'deleted' and label == section_label:
            deleted.add(section_label)
        # Whole section added/modified or paragraph added/deleted/modified
        else:
            modified.add(section_label)
    return modified, deleted
