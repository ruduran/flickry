import django_tables2 as tables

from .models import TagList


class TagListTable(tables.Table):
    tag_list = tables.LinkColumn('tag_list_images', args=[tables.A('pk')])
    delete = tables.TemplateColumn('<a href="{% url "delete" record.pk %}"><i class="fas fa-trash-alt"></i> Delete</a>')

    class Meta:
        model = TagList
        template_name = 'django_tables2/bootstrap.html'
        fields = ('tag_list', )
        show_header = False
