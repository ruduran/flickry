from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete


class TagList(models.Model):
    tag_list = models.CharField(max_length=200)
    load_finished = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.tag_list

    class Meta:
        ordering = ('tag_list',)


class Image(models.Model):
    image_id = models.BigIntegerField(unique=True, db_index=True)
    title = models.TextField()
    description = models.TextField()
    owner_name = models.CharField(max_length=128)
    image_url = models.CharField(max_length=128)
    image_page = models.CharField(max_length=128)
    owner_page = models.CharField(max_length=128)

    tag_lists = models.ManyToManyField(TagList, through='TagListImages')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title',)


class TagListImages(models.Model):
    tag_list = models.ForeignKey('TagList', on_delete=models.CASCADE)
    image = models.ForeignKey('Image', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('tag_list', 'image')


@receiver(pre_delete, sender=TagList)
def pre_delete_tag_list(sender, instance, **kwargs):
    for image in instance.image_set.all():
        if image.tag_lists.count() == 1:
            image.delete()
