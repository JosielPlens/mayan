from __future__ import absolute_import

from django.utils.translation import ugettext_lazy as _

from history.icons import icon_history_link
from history.permissions import PERMISSION_HISTORY_VIEW
from navigation.classes import Link

from .icons import (icon_documents, icon_document_delete,
    icon_document_properties, icon_document_edit, icon_document_preview,
    icon_document_download, icon_find_duplicates, icon_print, icon_version_revert,
    icon_version_compare, icon_versions, icon_document_types,
    icon_document_type_document_list, icon_document_update_page_count,
    icon_document_clear_image_cache, icon_document_page_view,
    icon_document_page_text, icon_document_page_edit,
    icon_document_page_navigation_next, icon_document_page_navigation_previous,
    icon_document_page_navigation_first, icon_document_page_navigation_last,
    icon_document_page_zoom_in, icon_document_page_zoom_out,
    icon_document_page_rotate_right, icon_document_page_rotate_left,
    icon_document_page_view_reset, icon_document_type_edit,
    icon_document_type_delete, icon_document_type_create,
    icon_document_type_filename_list, icon_document_type_filename_create,
    icon_document_type_filename_edit, icon_document_type_filename_delete,
    icon_document_missing_list)
from .permissions import (PERMISSION_DOCUMENT_CREATE,
    PERMISSION_DOCUMENT_PROPERTIES_EDIT, PERMISSION_DOCUMENT_VIEW,
    PERMISSION_DOCUMENT_DELETE, PERMISSION_DOCUMENT_DOWNLOAD,
    PERMISSION_DOCUMENT_TOOLS, PERMISSION_DOCUMENT_EDIT,
    PERMISSION_DOCUMENT_VERSION_REVERT, PERMISSION_DOCUMENT_TYPE_EDIT,
    PERMISSION_DOCUMENT_TYPE_DELETE, PERMISSION_DOCUMENT_TYPE_CREATE,
    PERMISSION_DOCUMENT_TYPE_VIEW, PERMISSION_DOCUMENT_NEW_VERSION)
from .settings import ZOOM_MAX_LEVEL, ZOOM_MIN_LEVEL


def is_first_page(context):
    return context['resolved_object'].is_first_page()


def is_last_page(context):
    return context['resolved_object'].is_last_page()


def is_min_zoom(context):
    return context['zoom'] <= ZOOM_MIN_LEVEL


def is_max_zoom(context):
    return context['zoom'] >= ZOOM_MAX_LEVEL


def is_current_version(context):
    return context['resolved_object'].is_latest_version()


document_list = Link(text=_(u'all documents'), view='document_list', icon=icon_documents)
document_list_recent = Link(text=_(u'recent documents'), view='document_list_recent', icon=icon_documents)
document_view_simple = Link(text=_(u'details'), view='document_view_simple', args='resolved_object.id', icon=icon_documents, permissions=[PERMISSION_DOCUMENT_VIEW])
# TODO rename document_view_advanced to document_info
document_view_advanced = Link(text=_(u'info'), view='document_view_advanced', args='resolved_object.id', icon=icon_document_properties, permissions=[PERMISSION_DOCUMENT_VIEW])
document_delete = Link(text=_(u'delete'), view='document_delete', args='resolved_object.id', icon=icon_document_delete, permissions=[PERMISSION_DOCUMENT_DELETE])
document_multiple_delete = Link(text=_(u'delete'), view='document_multiple_delete', icon=icon_document_delete, permissions=[PERMISSION_DOCUMENT_DELETE])
document_edit = Link(text=_(u'edit'), view='document_edit', args='resolved_object.id', icon=icon_document_edit, permissions=[PERMISSION_DOCUMENT_PROPERTIES_EDIT])
document_preview = Link(text=_(u'preview'), klass='fancybox', view='document_preview', args='resolved_object.id', icon=icon_document_preview, permissions=[PERMISSION_DOCUMENT_VIEW])

document_download = Link(text=_(u'download'), view='document_download', args='resolved_object.id', icon=icon_document_download, permissions=[PERMISSION_DOCUMENT_DOWNLOAD])
document_multiple_download = Link(text=_(u'download'), view='document_multiple_download', icon=icon_document_download, permissions=[PERMISSION_DOCUMENT_DOWNLOAD])
document_version_download = Link(text=_(u'download'), view='document_version_download', args='resolved_object.pk', icon=icon_document_download, permissions=[PERMISSION_DOCUMENT_DOWNLOAD])
document_find_duplicates = Link(text=_(u'find duplicates'), view='document_find_duplicates', args='resolved_object.id', icon=icon_find_duplicates, permissions=[PERMISSION_DOCUMENT_VIEW])
document_find_all_duplicates = Link(text=_(u'find all duplicates'), view='document_find_all_duplicates', icon=icon_find_duplicates, permissions=[PERMISSION_DOCUMENT_VIEW], description=_(u'Search all the documents\' checksums and return a list of the exact matches.'))
document_update_page_count = Link(text=_(u'update office documents\' page count'), view='document_update_page_count', icon=icon_document_update_page_count, permissions=[PERMISSION_DOCUMENT_TOOLS], description=_(u'Update the page count of the office type documents.  This is useful when enabling office document support after there were already office type documents in the database.'))
document_print = Link(text=_(u'print'), view='document_print', args='resolved_object.id', icon=icon_print, permissions=[PERMISSION_DOCUMENT_VIEW])
document_history_view = Link(text=_(u'history'), view='history_for_object', args=['"documents"', '"document"', 'resolved_object.pk'], icon=icon_history_link, permissions=[PERMISSION_HISTORY_VIEW])
document_missing_list = Link(text=_(u'Find missing document files'), view='document_missing_list', icon=icon_document_missing_list, description=_(u'Return a list of documents found on the database but that don\'t physically exist in the document storage.'), permissions=[PERMISSION_DOCUMENT_VIEW])

# Tools
document_clear_image_cache = Link(text=_(u'Clear the document image cache'), view='document_clear_image_cache', icon=icon_document_clear_image_cache, permissions=[PERMISSION_DOCUMENT_TOOLS], description=_(u'Clear the graphics representations used to speed up the documents\' display and interactive transformations results.'))

# Document pages
document_page_view = Link(text=_(u'page image'), klass='no-parent-history', view='document_page_view', args='resolved_object.pk', icon=icon_document_page_view, permissions=[PERMISSION_DOCUMENT_VIEW])
document_page_text = Link(text=_(u'page text'), klass='no-parent-history', view='document_page_text', args='resolved_object.pk', icon=icon_document_page_text, permissions=[PERMISSION_DOCUMENT_VIEW])
document_page_edit = Link(text=_(u'edit page text'), klass='no-parent-history', view='document_page_edit', args='resolved_object.pk', icon=icon_document_page_edit, permissions=[PERMISSION_DOCUMENT_EDIT])
document_page_navigation_next = Link(text=_(u'next page'), klass='no-parent-history', view='document_page_navigation_next', args='resolved_object.pk', icon=icon_document_page_navigation_next, permissions=[PERMISSION_DOCUMENT_VIEW], conditional_disable=is_last_page)
document_page_navigation_previous = Link(text=_(u'previous page'), klass='no-parent-history', view='document_page_navigation_previous', args='resolved_object.pk', icon=icon_document_page_navigation_previous, permissions=[PERMISSION_DOCUMENT_VIEW], conditional_disable=is_first_page)
document_page_navigation_first = Link(text=_(u'first page'), klass='no-parent-history', view='document_page_navigation_first', args='resolved_object.pk', icon=icon_document_page_navigation_first, permissions=[PERMISSION_DOCUMENT_VIEW], conditional_disable=is_first_page)
document_page_navigation_last = Link(text=_(u'last page'), klass='no-parent-history', view='document_page_navigation_last', args='resolved_object.pk', icon=icon_document_page_navigation_last, permissions=[PERMISSION_DOCUMENT_VIEW], conditional_disable=is_last_page)
document_page_zoom_in = Link(text=_(u'zoom in'), klass='no-parent-history', view='document_page_zoom_in', args='resolved_object.pk', icon=icon_document_page_zoom_in, permissions=[PERMISSION_DOCUMENT_VIEW], conditional_disable=is_max_zoom)
document_page_zoom_out = Link(text=_(u'zoom out'), klass='no-parent-history', view='document_page_zoom_out', args='resolved_object.pk', icon=icon_document_page_zoom_out, permissions=[PERMISSION_DOCUMENT_VIEW], conditional_disable=is_min_zoom)
document_page_rotate_right = Link(text=_(u'rotate right'), klass='no-parent-history', view='document_page_rotate_right', args='resolved_object.pk', icon=icon_document_page_rotate_right, permissions=[PERMISSION_DOCUMENT_VIEW])
document_page_rotate_left = Link(text=_(u'rotate left'), klass='no-parent-history', view='document_page_rotate_left', args='resolved_object.pk', icon=icon_document_page_rotate_left, permissions=[PERMISSION_DOCUMENT_VIEW])
document_page_view_reset = Link(text=_(u'reset view'), klass='no-parent-history', view='document_page_view_reset', args='resolved_object.pk', icon=icon_document_page_view_reset, permissions=[PERMISSION_DOCUMENT_VIEW])

# Document versions
document_version_list = Link(text=_(u'versions'), view='document_version_list', args='resolved_object.pk', icon=icon_versions, permissions=[PERMISSION_DOCUMENT_VIEW])
document_version_revert = Link(text=_(u'revert'), view='document_version_revert', args='resolved_object.pk', icon=icon_version_revert, permissions=[PERMISSION_DOCUMENT_VERSION_REVERT], conditional_disable=is_current_version)

# Document type related links
document_type_list = Link(text=_(u'document type list'), view='document_type_list', icon=icon_document_types, permissions=[PERMISSION_DOCUMENT_TYPE_VIEW])
document_type_setup = Link(text=_(u'document types'), view='document_type_list', icon=icon_document_types, permissions=[PERMISSION_DOCUMENT_TYPE_VIEW], children_view_regex=[r'^document_type_'])
document_type_document_list = Link(text=_(u'documents of this type'), view='document_type_document_list', args='resolved_object.id', icon=icon_document_type_document_list, permissions=[PERMISSION_DOCUMENT_TYPE_VIEW])
document_type_edit = Link(text=_(u'edit'), view='document_type_edit', args='resolved_object.id', icon=icon_document_type_edit, permissions=[PERMISSION_DOCUMENT_TYPE_EDIT])
document_type_delete = Link(text=_(u'delete'), view='document_type_delete', args='resolved_object.id', icon=icon_document_type_delete, permissions=[PERMISSION_DOCUMENT_TYPE_DELETE])
document_type_create = Link(text=_(u'create document type'), view='document_type_create', icon=icon_document_type_create, permissions=[PERMISSION_DOCUMENT_TYPE_CREATE])

document_type_filename_list = Link(text=_(u'filenames'), view='document_type_filename_list', args='resolved_object.id', icon=icon_document_type_filename_list, permissions=[PERMISSION_DOCUMENT_TYPE_VIEW])
document_type_filename_create = Link(text=_(u'add filename to document type'), view='document_type_filename_create', args='document_type.id', icon=icon_document_type_filename_create, permissions=[PERMISSION_DOCUMENT_TYPE_EDIT])
document_type_filename_edit = Link(text=_(u'edit'), view='document_type_filename_edit', args='resolved_object.id', icon=icon_document_type_filename_edit, permissions=[PERMISSION_DOCUMENT_TYPE_EDIT])
document_type_filename_delete = Link(text=_(u'delete'), view='document_type_filename_delete', args='resolved_object.id', icon=icon_document_type_filename_delete, permissions=[PERMISSION_DOCUMENT_TYPE_EDIT])

link_documents_menu = Link(icon=icon_documents, text=_(u'documents'), view='document_list_recent',
    children_url_regex=[r'^documents/[^t]', r'^metadata/[^s]', r'comments', r'tags/document', r'grouping/[^s]', r'history/list/for_resolved_object/documents'],
    children_view_regex=[r'document_acl', r'smart_link_instance'],
    children_views=['document_folder_list', 'folder_add_document', 'document_index_list', 'upload_version', ])
