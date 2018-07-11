from django.urls import path

from . import views

urlpatterns = [
    path('', views.tag_lists, name='tag_lists'),
    path('images/<int:tag_list_id>/', views.ImagesByTagsView.as_view(), name='tag_list_images'),
    path('images/<str:field>/', views.ImagesByFieldView.as_view(), name='images_by_field'),
    path('add/', views.add, name='add'),
    path('delete/<int:tag_list_id>', views.delete, name='delete'),
]
