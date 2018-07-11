from django.test import TestCase

from imagesbytags.models import Image, TagList, TagListImages


class TagListTests(TestCase):

    def test_str(self):
        tag_list = TagList(tag_list='tag,list')
        self.assertEqual(tag_list.tag_list, str(tag_list))


class ImageTests(TestCase):

    def test_str(self):
        image = Image(image_id=1,
                      title='title',
                      description='description',
                      owner_name='ownername',
                      image_url='url',
                      image_page='image_page',
                      owner_page='owner_page')
        self.assertEqual(image.title, str(image))


class ModelsTests(TestCase):
    def setUp(self):
        self.tag_list = TagList(tag_list='tag,list')
        self.tag_list.save()
        self.tag_list2 = TagList(tag_list='tag,list,2')
        self.tag_list2.save()

        self.image1 = Image(image_id=1,
                            title='image1',
                            description='description',
                            owner_name='ownername',
                            image_url='url',
                            image_page='image_page',
                            owner_page='owner_page')
        self.image1.save()
        TagListImages.objects.get_or_create(tag_list=self.tag_list,
                                            image=self.image1)

        self.image2 = Image(image_id=2,
                            title='image2',
                            description='description',
                            owner_name='ownername',
                            image_url='url',
                            image_page='image_page',
                            owner_page='owner_page')
        self.image2.save()
        TagListImages.objects.get_or_create(tag_list=self.tag_list,
                                            image=self.image2)
        self.image3 = Image(image_id=3,
                            title='image3',
                            description='description',
                            owner_name='ownername',
                            image_url='url',
                            image_page='image_page',
                            owner_page='owner_page')
        self.image3.save()
        TagListImages.objects.get_or_create(tag_list=self.tag_list2,
                                            image=self.image3)

    def tearDown(self):
        if self.tag_list.id:
            self.tag_list.delete()
        self.image1.delete()
        self.image2.delete()
        if self.tag_list2.id:
            self.tag_list2.delete()
        self.image3.delete()

    def test_images_deleted_upon_tag_list_deletion(self):
        self.assertEqual(Image.objects.count(), 3)
        self.tag_list.delete()
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(Image.objects.all()[0], self.image3)
