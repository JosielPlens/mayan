from __future__ import absolute_import

import tempfile

from django.utils.translation import ugettext_lazy as _

from acls.api import class_permissions
from common.utils import validate_path, encapsulate
from converter.classes import MenuLessObject
from diagnostics.api import DiagnosticNamespace
from dynamic_search.classes import SearchModel
from history.permissions import PERMISSION_HISTORY_VIEW
from maintenance.classes import MaintenanceNamespace
from navigation.api import (register_top_menu,
    register_model_list_columns, register_multi_item_links,
    register_sidebar_template)
from navigation.classes import Combined, Link
from project_setup.api import register_setup
from statistics.classes import StatisticNamespace

from .links import (document_list, document_list_recent,
    document_view_simple, document_view_advanced,
    document_delete, document_multiple_delete, document_edit, document_download,
    document_multiple_download, document_version_download,
    document_find_duplicates, document_find_all_duplicates, document_update_page_count,
    document_print, document_history_view, document_missing_list, document_clear_image_cache,
    document_page_view, document_page_text, document_page_edit, document_page_navigation_next,
    document_page_navigation_previous, document_page_navigation_first,
    document_page_navigation_last, document_page_zoom_in, document_page_zoom_out,
    document_page_rotate_right, document_page_rotate_left,
    document_page_view_reset, document_version_list, document_version_revert,
    document_type_list, document_type_setup, document_type_document_list,
    document_type_edit, document_type_delete, document_type_create,
    document_type_filename_list, document_type_filename_create, document_type_filename_edit,
    document_type_filename_delete, link_documents_menu)
from .models import (Document, DocumentPage, DocumentType, DocumentTypeFilename,
    DocumentVersion)
from .permissions import (PERMISSION_DOCUMENT_PROPERTIES_EDIT,
    PERMISSION_DOCUMENT_VIEW, PERMISSION_DOCUMENT_DELETE,
    PERMISSION_DOCUMENT_DOWNLOAD, PERMISSION_DOCUMENT_EDIT,
    PERMISSION_DOCUMENT_VERSION_REVERT, PERMISSION_DOCUMENT_NEW_VERSION)
import documents.settings as document_settings
from .statistics import DocumentStatistics, DocumentUsageStatistics
from .widgets import document_thumbnail

# Register document type links
Link.bind_links([DocumentType], [document_type_edit, document_type_delete, document_type_document_list, document_type_filename_list])
Link.bind_links([DocumentTypeFilename], [document_type_filename_edit, document_type_filename_delete])

Link.bind_links(['setup_document_type_metadata', 'document_type_filename_delete', 'document_type_create', 'document_type_filename_create', 'document_type_filename_edit', 'document_type_filename_list', 'document_type_list', 'document_type_document_list', 'document_type_edit', 'document_type_delete'], [document_type_list, document_type_create], menu_name='secondary_menu')
Link.bind_links([DocumentTypeFilename, 'document_type_filename_list', 'document_type_filename_create'], [document_type_filename_create], menu_name='sidebar')

# Register document links
Link.bind_links([Document], [document_view_simple, document_view_advanced, document_edit, document_print, document_delete, document_download, document_find_duplicates])
register_multi_item_links(['document_find_duplicates', 'folder_view', 'index_instance_node_view', 'document_type_document_list', 'search', 'results', 'document_group_view', 'document_list', 'document_list_recent', 'tag_tagged_item_list'], [document_multiple_delete, document_multiple_download])

# Document Version links
Link.bind_links([DocumentVersion], [document_version_revert, document_version_download])

secondary_menu_links = [document_list_recent, document_list]

Link.bind_links(['document_list_recent', 'document_list', 'document_create', 'upload_interactive', 'staging_file_delete'], secondary_menu_links, menu_name='secondary_menu')
Link.bind_links([Document], secondary_menu_links, menu_name='secondary_menu')

# Document page links
Link.bind_links([DocumentPage], [
    document_page_view,
    document_page_text, document_page_edit,
])

# Document page navigation links
Link.bind_links([DocumentPage], [
    document_page_navigation_first, document_page_navigation_previous,
    document_page_navigation_next, document_page_navigation_last
], menu_name='secondary_menu')

# Document page rotation and zoom links
Link.bind_links([Combined(DocumentPage, 'document_page_view')], [
    document_page_rotate_left, document_page_rotate_right, document_page_zoom_in,
    document_page_zoom_out, document_page_view_reset
], menu_name='form_header')

# Don't show menus when showing this objects' tranformaton views
MenuLessObject(DocumentPage)

diagnostics_namespace = DiagnosticNamespace(_(u'documents'))
diagnostics_namespace.create_tool(document_missing_list)

namespace = MaintenanceNamespace(_(u'documents'))
namespace.create_tool(document_find_all_duplicates)
namespace.create_tool(document_update_page_count)
namespace.create_tool(document_clear_image_cache)

register_model_list_columns(Document, [
    {'name': _(u'thumbnail'), 'attribute':
        encapsulate(lambda x: document_thumbnail(x, gallery_name='document_list', title=x.filename))
    },
])

register_top_menu(
    'documents',
    link=link_documents_menu,
    position=1
)

register_sidebar_template(['document_list_recent'], 'recent_document_list_help.html')
register_sidebar_template(['document_type_list'], 'document_types_help.html')

Link.bind_links([Document], [document_view_simple], menu_name='form_header', position=0)
Link.bind_links([Document], [document_view_advanced], menu_name='form_header', position=1)
Link.bind_links([Document], [document_history_view], menu_name='form_header')
Link.bind_links([Document], [document_version_list], menu_name='form_header')

if (validate_path(document_settings.CACHE_PATH) is False) or (not document_settings.CACHE_PATH):
    setattr(document_settings, 'CACHE_PATH', tempfile.mkdtemp())

register_setup(document_type_setup)

class_permissions(Document, [
    PERMISSION_DOCUMENT_PROPERTIES_EDIT,
    PERMISSION_DOCUMENT_EDIT,
    PERMISSION_DOCUMENT_VIEW,
    PERMISSION_DOCUMENT_DELETE,
    PERMISSION_DOCUMENT_DOWNLOAD,
    PERMISSION_DOCUMENT_NEW_VERSION,
    PERMISSION_DOCUMENT_VERSION_REVERT,
    PERMISSION_HISTORY_VIEW
])

document_search = SearchModel('documents', 'Document', permission=PERMISSION_DOCUMENT_VIEW)
document_search.add_model_field('document_type__name', label=_(u'Document type'))
document_search.add_model_field('documentversion__mimetype', label=_(u'MIME type'))
document_search.add_model_field('documentversion__filename', label=_(u'Filename'))
document_search.add_model_field('documentmetadata__metadata_type__name', label=_(u'Metadata type'))
document_search.add_model_field('documentmetadata__value', label=_(u'Metadata value'))
document_search.add_model_field('documentversion__documentpage__content', label=_(u'Content'))
document_search.add_model_field('description', label=_(u'Description'))
document_search.add_model_field('tags__name', label=_(u'Tags'))
document_search.add_related_field('comments', 'Comment', 'comment', 'object_pk', label=_(u'Comments'))

namespace = StatisticNamespace(name='documents', label=_(u'Documents'))
namespace.add_statistic(DocumentStatistics(name='document_stats', label=_(u'Document tendencies')))
namespace.add_statistic(DocumentUsageStatistics(name='document_usage', label=_(u'Document usage')))
