from __future__ import absolute_import

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.views.generic.list_detail import object_list
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

from permissions.models import Permission
from documents.models import Document
from documents.widgets import document_link, document_thumbnail
from common.utils import encapsulate
from acls.models import AccessEntry
from job_processor.exceptions import JobQueuePushError

from .permissions import (PERMISSION_OCR_DOCUMENT,
    PERMISSION_OCR_DOCUMENT_DELETE, PERMISSION_OCR_QUEUE_ENABLE_DISABLE,
    PERMISSION_OCR_CLEAN_ALL_PAGES, PERMISSION_OCR_QUEUE_EDIT)
from .models import OCRProcessingSingleton
from .exceptions import (AlreadyQueued, ReQueueError, OCRProcessingAlreadyDisabled,
    OCRProcessingAlreadyEnabled)
from .api import clean_pages
from . import ocr_job_queue, ocr_job_type


def ocr_log(request):
    Permission.objects.check_permissions(request.user, [PERMISSION_OCR_DOCUMENT])

    context = {
        'queue': OCRProcessingSingleton.get(),
        'object_name': _(u'OCR processing'),  # TODO fix, not working
        'navigation_object_name': 'queue',
        'object_list': [],
        'title': _(u'OCR log items'),
        #'hide_object': True,
        #'hide_link': True,
        'extra_columns': [
            {'name': _(u'document'), 'attribute': encapsulate(lambda x: document_link(x.document_version.document) if hasattr(x, 'document_version') else _(u'Missing document.'))},
            {'name': _(u'version'), 'attribute': 'document_version'},
            {'name': _(u'thumbnail'), 'attribute': encapsulate(lambda x: document_thumbnail(x.document_version.document))},
            {'name': _('submitted'), 'attribute': encapsulate(lambda x: unicode(x.datetime_submitted).split('.')[0]), 'keep_together':True},
            #{'name': _('delay'), 'attribute': 'delay'},
            #{'name': _('state'), 'attribute': encapsulate(lambda x: x.get_state_display())},
            #{'name': _('node'), 'attribute': 'node_name'},
            {'name': _('result'), 'attribute': 'result'},
        ],
        'multi_select_as_buttons': True,
        'sidebar_subtemplates_list': [
            {
                'name': 'generic_subtemplate.html',
                'context': {
                    'side_bar': True,
                    'title': _(u'OCR processing properties'),
                    'content': _(u'Current state: %s') % OCRProcessingSingleton.get().get_state_display(),
                }
            }
        ]
    }

    return render_to_response('generic_list.html', context,
        context_instance=RequestContext(request))

    #        'queue': document_queue,
    #        'object_name': _(u'document queue'),
    #        'navigation_object_name': 'queue',
    #        'list_object_variable_name': 'queue_document',
    #    },
    #)


def ocr_disable(request):
    Permission.objects.check_permissions(request.user, [PERMISSION_OCR_QUEUE_ENABLE_DISABLE])

    next = request.POST.get('next', request.GET.get('next', request.META.get('HTTP_REFERER', None)))
    previous = request.POST.get('previous', request.GET.get('previous', request.META.get('HTTP_REFERER', None)))

    if request.method == 'POST':
        try:
            OCRProcessingSingleton.get().disable()
        except OCRProcessingAlreadyDisabled:
            messages.warning(request, _(u'OCR processing already disabled.'))
            return HttpResponseRedirect(previous)            
        else:
            messages.success(request, _(u'OCR processing disabled successfully.'))
            return HttpResponseRedirect(next)

    return render_to_response('generic_confirm.html', {
        'queue': OCRProcessingSingleton.get(),
        'navigation_object_name': 'queue',
        'title': _(u'Are you sure you wish to disable OCR processing?'),
        'next': next,
        'previous': previous,
        'form_icon': u'control_stop_blue.png',
    }, context_instance=RequestContext(request))


def ocr_enable(request):
    Permission.objects.check_permissions(request.user, [PERMISSION_OCR_QUEUE_ENABLE_DISABLE])

    next = request.POST.get('next', request.GET.get('next', request.META.get('HTTP_REFERER', None)))
    previous = request.POST.get('previous', request.GET.get('previous', request.META.get('HTTP_REFERER', None)))

    if request.method == 'POST':
        try:
            OCRProcessingSingleton.get().enable()
        except OCRProcessingAlreadyDisabled:
            messages.warning(request, _(u'OCR processing already enabled.'))
            return HttpResponseRedirect(previous)            
        else:
            messages.success(request, _(u'OCR processing enabled successfully.'))
            return HttpResponseRedirect(next)

    return render_to_response('generic_confirm.html', {
        'queue': OCRProcessingSingleton.get(),
        'navigation_object_name': 'queue',
        'title': _(u'Are you sure you wish to enable OCR processing?'),
        'next': next,
        'previous': previous,
        'form_icon': u'control_play_blue.png',
    }, context_instance=RequestContext(request))



def queue_document_delete(request, queue_document_id=None, queue_document_id_list=None):
    Permission.objects.check_permissions(request.user, [PERMISSION_OCR_DOCUMENT_DELETE])

    if queue_document_id:
        queue_documents = [get_object_or_404(QueueDocument, pk=queue_document_id)]
    elif queue_document_id_list:
        queue_documents = [get_object_or_404(QueueDocument, pk=queue_document_id) for queue_document_id in queue_document_id_list.split(',')]
    else:
        messages.error(request, _(u'Must provide at least one queue document.'))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    next = request.POST.get('next', request.GET.get('next', request.META.get('HTTP_REFERER', None)))
    previous = request.POST.get('previous', request.GET.get('previous', request.META.get('HTTP_REFERER', None)))

    if request.method == 'POST':
        for queue_document in queue_documents:
            try:
                if queue_document.state == QUEUEDOCUMENT_STATE_PROCESSING:
                    messages.error(request, _(u'Document: %s is being processed and can\'t be deleted.') % queue_document)
                else:
                    queue_document.delete()
                    messages.success(request, _(u'Queue document: %(document)s deleted successfully.') % {
                        'document': queue_document.document})

            except Exception, e:
                messages.error(request, _(u'Error deleting document: %(document)s; %(error)s') % {
                    'document': queue_document, 'error': e})
        return HttpResponseRedirect(next)

    context = {
        'next': next,
        'previous': previous,
        'delete_view': True,
        'form_icon': u'hourglass_delete.png',
    }

    if len(queue_documents) == 1:
        context['object'] = queue_documents[0]
        context['title'] = _(u'Are you sure you wish to delete queue document: %s?') % ', '.join([unicode(d) for d in queue_documents])
    elif len(queue_documents) > 1:
        context['title'] = _(u'Are you sure you wish to delete queue documents: %s?') % ', '.join([unicode(d) for d in queue_documents])

    return render_to_response('generic_confirm.html', context,
        context_instance=RequestContext(request))


def queue_document_multiple_delete(request):
    return queue_document_delete(request, queue_document_id_list=request.GET.get('id_list', ''))


def submit_document_multiple(request):
    for item_id in request.GET.get('id_list', '').split(','):
        submit_document(request, item_id)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def submit_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    try:
        Permission.objects.check_permissions(request.user, [PERMISSION_OCR_DOCUMENT])
    except PermissionDenied:
        AccessEntry.objects.check_access(PERMISSION_OCR_DOCUMENT, request.user, document)

    return submit_document_to_queue(request, document=document,
        post_submit_redirect=request.META.get('HTTP_REFERER', '/'))


def submit_document_to_queue(request, document, post_submit_redirect=None):
    """
    This view is meant to be reusable
    """

    try:
        ocr_job_queue.push(ocr_job_type, document_version_pk=document.latest_version.pk)
        messages.success(request, _(u'Document: %(document)s was added to the OCR queue sucessfully.') % {
            'document': document})
    except JobQueuePushError:
        messages.warning(request, _(u'Document: %(document)s is already queued.') % {
        'document': document})
    except Exception, e:
        messages.error(request, e)

    if post_submit_redirect:
        return HttpResponseRedirect(post_submit_redirect)


def re_queue_document(request, queue_document_id=None, queue_document_id_list=None):
    Permission.objects.check_permissions(request.user, [PERMISSION_OCR_DOCUMENT])

    if queue_document_id:
        queue_documents = [get_object_or_404(QueueDocument, pk=queue_document_id)]
    elif queue_document_id_list:
        queue_documents = [get_object_or_404(QueueDocument, pk=queue_document_id) for queue_document_id in queue_document_id_list.split(',')]
    else:
        messages.error(request, _(u'Must provide at least one queue document.'))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    next = request.POST.get('next', request.GET.get('next', request.META.get('HTTP_REFERER', None)))
    previous = request.POST.get('previous', request.GET.get('previous', request.META.get('HTTP_REFERER', None)))

    if request.method == 'POST':
        for queue_document in queue_documents:
            try:
                queue_document.requeue()
                messages.success(
                    request,
                    _(u'Document: %(document)s was re-queued to the OCR queue: %(queue)s') % {
                        'document': queue_document.document_version.document,
                        'queue': queue_document.document_queue.label
                    }
                )
            except Document.DoesNotExist:
                messages.error(request, _(u'Document no longer in queue.'))
            except ReQueueError:
                messages.warning(
                    request,
                    _(u'Document: %s is already being processed and can\'t be re-queded.') % queue_document
                )
        return HttpResponseRedirect(next)

    context = {
        'next': next,
        'previous': previous,
        'form_icon': u'hourglass_add.png',
    }

    if len(queue_documents) == 1:
        context['object'] = queue_documents[0]
        context['title'] = _(u'Are you sure you wish to re-queue document: %s?') % ', '.join([unicode(d) for d in queue_documents])
    elif len(queue_documents) > 1:
        context['title'] = _(u'Are you sure you wish to re-queue documents: %s?') % ', '.join([unicode(d) for d in queue_documents])

    return render_to_response('generic_confirm.html', context,
        context_instance=RequestContext(request))


def re_queue_multiple_document(request):
    return re_queue_document(request, queue_document_id_list=request.GET.get('id_list', []))


def all_document_ocr_cleanup(request):
    Permission.objects.check_permissions(request.user, [PERMISSION_OCR_CLEAN_ALL_PAGES])

    previous = request.POST.get('previous', request.GET.get('previous', request.META.get('HTTP_REFERER', None)))
    next = request.POST.get('next', request.GET.get('next', request.META.get('HTTP_REFERER', None)))

    if request.method != 'POST':
        return render_to_response('generic_confirm.html', {
            'previous': previous,
            'next': next,
            'title': _(u'Are you sure you wish to clean up all the pages content?'),
            'message': _(u'On large databases this operation may take some time to execute.'),
            'form_icon': u'text_strikethroungh.png',
        }, context_instance=RequestContext(request))
    else:
        try:
            clean_pages()
            messages.success(request, _(u'Document pages content clean up complete.'))
        except Exception, e:
            messages.error(request, _(u'Document pages content clean up error: %s') % e)

        return HttpResponseRedirect(next)


def display_link(obj):
    output = []
    if hasattr(obj, 'get_absolute_url'):
        output.append(u'<a href="%(url)s">%(obj)s</a>' % {
            'url': obj.get_absolute_url(),
            'obj': obj
        })
    if output:
        return u''.join(output)
    else:
        return obj


# Setup views
def setup_queue_transformation_list(request, document_queue_id):
    Permission.objects.check_permissions(request.user, [PERMISSION_OCR_QUEUE_EDIT])

    document_queue = get_object_or_404(DocumentQueue, pk=document_queue_id)

    context = {
        'object_list': QueueTransformation.transformations.get_for_object(document_queue),
        'title': _(u'transformations for: %s') % document_queue,
        'queue': document_queue,
        'object_name': _(u'document queue'),
        'navigation_object_name': 'queue',
        'list_object_variable_name': 'transformation',
        'extra_columns': [
            {'name': _(u'order'), 'attribute': 'order'},
            {'name': _(u'transformation'), 'attribute': encapsulate(lambda x: x.get_transformation_display())},
            {'name': _(u'arguments'), 'attribute': 'arguments'}
            ],
        'hide_link': True,
        'hide_object': True,
    }

    return render_to_response('generic_list.html', context,
        context_instance=RequestContext(request))


def setup_queue_transformation_edit(request, transformation_id):
    Permission.objects.check_permissions(request.user, [PERMISSION_OCR_QUEUE_EDIT])

    transformation = get_object_or_404(QueueTransformation, pk=transformation_id)
    redirect_view = reverse('setup_queue_transformation_list', args=[transformation.content_object.pk])
    next = request.POST.get('next', request.GET.get('next', request.META.get('HTTP_REFERER', redirect_view)))

    if request.method == 'POST':
        form = QueueTransformationForm(instance=transformation, data=request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, _(u'Queue transformation edited successfully'))
                return HttpResponseRedirect(next)
            except Exception, e:
                messages.error(request, _(u'Error editing queue transformation; %s') % e)
    else:
        form = QueueTransformationForm(instance=transformation)

    return render_to_response('generic_form.html', {
        'title': _(u'Edit transformation: %s') % transformation,
        'form': form,
        'queue': transformation.content_object,
        'transformation': transformation,
        'navigation_object_list': [
            {'object': 'queue', 'name': _(u'document queue')},
            {'object': 'transformation', 'name': _(u'transformation')}
        ],
        'next': next,
    },
    context_instance=RequestContext(request))


def setup_queue_transformation_delete(request, transformation_id):
    Permission.objects.check_permissions(request.user, [PERMISSION_OCR_QUEUE_EDIT])

    transformation = get_object_or_404(QueueTransformation, pk=transformation_id)
    redirect_view = reverse('setup_queue_transformation_list', args=[transformation.content_object.pk])
    previous = request.POST.get('previous', request.GET.get('previous', request.META.get('HTTP_REFERER', redirect_view)))

    if request.method == 'POST':
        try:
            transformation.delete()
            messages.success(request, _(u'Queue transformation deleted successfully.'))
        except Exception, e:
            messages.error(request, _(u'Error deleting queue transformation; %(error)s') % {
                'error': e}
            )
        return HttpResponseRedirect(redirect_view)

    return render_to_response('generic_confirm.html', {
        'delete_view': True,
        'transformation': transformation,
        'queue': transformation.content_object,
        'navigation_object_list': [
            {'object': 'queue', 'name': _(u'document queue')},
            {'object': 'transformation', 'name': _(u'transformation')}
        ],
        'title': _(u'Are you sure you wish to delete queue transformation "%(transformation)s"') % {
            'transformation': transformation.get_transformation_display(),
        },
        'previous': previous,
        'form_icon': u'shape_square_delete.png',
    },
    context_instance=RequestContext(request))


def setup_queue_transformation_create(request, document_queue_id):
    Permission.objects.check_permissions(request.user, [PERMISSION_OCR_QUEUE_EDIT])

    document_queue = get_object_or_404(DocumentQueue, pk=document_queue_id)

    redirect_view = reverse('setup_queue_transformation_list', args=[document_queue.pk])

    if request.method == 'POST':
        form = QueueTransformationForm_create(request.POST)
        if form.is_valid():
            try:
                queue_tranformation = form.save(commit=False)
                queue_tranformation.content_object = document_queue
                queue_tranformation.save()
                messages.success(request, _(u'Queue transformation created successfully'))
                return HttpResponseRedirect(redirect_view)
            except Exception, e:
                messages.error(request, _(u'Error creating queue transformation; %s') % e)
    else:
        form = QueueTransformationForm_create()

    return render_to_response('generic_form.html', {
        'form': form,
        'queue': document_queue,
        'object_name': _(u'document queue'),
        'navigation_object_name': 'queue',
        'title': _(u'Create new transformation for queue: %s') % document_queue,
    }, context_instance=RequestContext(request))
