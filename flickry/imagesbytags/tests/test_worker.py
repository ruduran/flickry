from unittest.mock import MagicMock, patch

from django.test import TestCase

from imagesbytags.worker import WorkerThread, SingletonMetaclass, Worker


class WorkerThreadTests(TestCase):
    @patch('imagesbytags.worker.FlickrAPI')
    def setUp(self, flickrapi_mock):
        self.worker_thread = WorkerThread(MagicMock(), MagicMock(), MagicMock())

    @patch('imagesbytags.worker.TagList')
    def test_load_images(self, tag_list_mock):
        self.worker_thread.is_ignored = MagicMock(return_value=False)
        self.worker_thread.store_image = MagicMock()

        photos = {
            'photos': {
                'photo': [
                    'image1',
                    'image2'
                ],
                'pages': 1
            },
            'stat': 'ok'
        }
        self.worker_thread.flickr.photos.search.return_value = photos

        self.worker_thread.load_images()

        self.worker_thread.is_ignored.assert_called_once()
        self.worker_thread.flickr.photos.search.assert_called_once()
        self.assertEqual(2, self.worker_thread.store_image.call_count)

    @patch('imagesbytags.worker.TagList')
    def test_load_images_for_ignored_tag(self, tag_list_mock):
        self.worker_thread.is_ignored = MagicMock(return_value=True)
        self.worker_thread.store_image = MagicMock()

        self.worker_thread.load_images()

        self.worker_thread.is_ignored.assert_called_once()
        self.worker_thread.flickr.photos.search.assert_not_called()
        self.worker_thread.store_image.assert_not_called()


class SingletonMetaclassTests(TestCase):
    def test_singleton(self):
        class Test(metaclass=SingletonMetaclass):
            x = 0

        t1 = Test()
        t2 = Test()
        t1.x = 1
        t2.x = 2

        self.assertEqual(t1.x, t2.x)
        self.assertEqual(2, t1.x)


class WorkerTests(TestCase):
    def setUp(self):
        self.worker = Worker()
        self.worker._input_queue = MagicMock()
        self.worker._ignore_queue = MagicMock()
        self.worker._load_lock = MagicMock()
        self.worker._worker = MagicMock()

    def test_start(self):
        self.worker._worker.is_alive.return_value = False
        self.worker.start()
        self.worker._worker.start.assert_called()

    def test_start_already_started(self):
        self.worker._worker.is_alive.return_value = True
        self.worker.start()
        self.worker._worker.start.assert_not_called()

    def test_load_tag_list_images(self):
        tag_list_id = 'id'
        self.worker.load_tag_list_images(tag_list_id)
        self.worker._input_queue.put.assert_called_with(tag_list_id)

    def test_ignore_tag_list(self):
        tag_list_id = 'id'
        self.worker.ignore_tag_list(tag_list_id)
        self.worker._ignore_queue.put.assert_called_with(tag_list_id)
        self.worker._load_lock.__enter__.assert_called()
