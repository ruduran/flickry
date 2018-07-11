import threading
import queue
import time


from django.db.utils import IntegrityError
from django.conf import settings

from flickrapi import FlickrAPI

from .models import Image, TagList, TagListImages


class WorkerThread(threading.Thread):
    def __init__(self, input_q, ignore_q, lock):
        super().__init__()
        self.input_q = input_q
        self.ignore_q = ignore_q
        self.lock = lock

        self.stop = threading.Event()

        self.current_tag_list = ''
        self.tag_lists_to_ignore = set()

        self.flickr = FlickrAPI(settings.FLICKR.get('KEY'), settings.FLICKR.get('SECRET'), format='parsed-json')

    def run(self):
        while not self.stop.isSet():
            try:
                self.current_tag_list = self.input_q.get(block=False)
                self.load_images()
            except queue.Empty:
                time.sleep(1)
                continue

    def stop(self, timeout=None):
        self.stop.set()
        super().join(timeout)

    def is_ignored(self, tag_list_id):
        try:
            while True:
                self.tag_lists_to_ignore.add(self.ignore_q.get(block=False))
        except queue.Empty:
            pass  # Nothing left

        ignored = tag_list_id in self.tag_lists_to_ignore
        self.tag_lists_to_ignore.discard(tag_list_id)
        return ignored

    def load_images(self):
        try:
            tag_list = TagList.objects.get(pk=self.current_tag_list)
        except TagList.DoesNotExist:
            return

        load_finished = False
        page = 1
        while not load_finished:
            with self.lock:
                if self.is_ignored(tag_list.id):
                    return

                photos = self.flickr.photos.search(tags=tag_list, tag_mode='all',
                                                   per_page=100, page=page,
                                                   extras='description,owner_name,tags,url_l,url_m')
                if not photos or photos.get('stat') != 'ok':
                    return

                for photo in photos.get('photos', {}).get('photo', []):
                    self.store_image(tag_list, photo)

                pages = photos.get('photos', {}).get('pages', 0)
                if page >= pages:
                    load_finished = True
                else:
                    page += 1

        tag_list.load_finished = load_finished
        tag_list.save()

    def store_image(self, tag_list, image_data):
        user_id = image_data.get('owner')
        image_id = int(image_data.get('id'))
        image_url = image_data.get('url_l', '')
        if not image_url:
            image_url = image_data.get('url_m', '')

        image_data = {
            'image_id': image_id,
            'title': image_data.get('title'),
            'description': image_data.get('description', {}).get('_content', ''),
            'owner_name': image_data.get('ownername', ''),
            'image_url': image_url,
            'image_page': 'https://www.flickr.com/photos/{}/{}'.format(user_id, image_id),
            'owner_page': 'https://www.flickr.com/photos/{}/'.format(user_id),
        }
        image = Image(**image_data)
        try:
            image.save()
        except IntegrityError:
            image = Image.objects.get(image_id=image_id)

        TagListImages.objects.get_or_create(tag_list=tag_list, image=image)


class SingletonMetaclass(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)

        return cls._instances[cls]


class Worker(metaclass=SingletonMetaclass):
    def __init__(self):
        self._input_queue = queue.Queue()
        self._ignore_queue = queue.Queue()
        self._load_lock = threading.Lock()
        self._worker = WorkerThread(self._input_queue, self._ignore_queue, self._load_lock)

    def start(self):
        if self._worker.is_alive():
            return

        pending_loads = TagList.objects.filter(load_finished=False)
        for tag_list in pending_loads:
            self.load_tag_list_images(tag_list.id)

        self._worker.start()

    def load_tag_list_images(self, tag_list_id):
        self._input_queue.put(tag_list_id)

    def ignore_tag_list(self, tag_list_id):
        self._ignore_queue.put(tag_list_id)
        with self._load_lock:
            # Just wait for the lock to return
            pass
