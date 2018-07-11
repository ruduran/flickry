import threading

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.list import ListView
from django_tables2 import RequestConfig

from .models import TagList, Image
from .tables import TagListTable
from .worker import Worker


class ImagesByTagsView(ListView):
    model = Image
    paginate_by = 10

    def get_queryset(self):
        return Image.objects.order_by('pk').filter(tag_lists=self.kwargs['tag_list_id'])


class ImagesByFieldView(ListView):
    model = Image
    paginate_by = 10
    valid_fields = ('title', 'description', 'owner_name')

    def get_queryset(self):
        field = self.kwargs['field']
        if field not in self.valid_fields:
            raise Http404('Not a valid field to look for.')

        args = {'{}__icontains'.format(field): self.request.GET.get(field)}
        return Image.objects.order_by('pk').filter(**args)


def tag_lists(request):
    table = TagListTable(TagList.objects.filter(deleted=False))
    RequestConfig(request).configure(table)
    return render(request, 'imagesbytags/tag_lists.html', {'table': table})


def add(request):
    if request.POST.get('tag_list'):
        tag_list = request.POST['tag_list']

        tag_list_object = TagList(tag_list=tag_list)
        tag_list_object.save()
        w = Worker()
        w.load_tag_list_images(tag_list_object.id)

    return HttpResponseRedirect(reverse('tag_lists'))


class DeleteThread(threading.Thread):
    def __init__(self, tag_list_id):
        super().__init__()
        self.tag_list_id = tag_list_id

    def run(self):
        w = Worker()
        w.ignore_tag_list(self.tag_list_id)
        try:
            tag_list = TagList.objects.get(pk=self.tag_list_id)
            tag_list.delete()
        except TagList.DoesNotExist:
            pass


def delete(request, tag_list_id):
    try:
        tag_list = TagList.objects.get(pk=tag_list_id)
        tag_list.deleted = True
        tag_list.save()
    except TagList.DoesNotExist:
        pass

    dth = DeleteThread(tag_list_id)
    dth.start()

    return HttpResponseRedirect(reverse('tag_lists'))
