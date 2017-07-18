'''
@author: lefterav
'''

from django.conf.urls import url

from . import views

app_name = 'qe'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^task/(?P<task_id>[0-9]+)/document/(?P<document_id>[0-9]+)$', 
        views.document, 
        name='document'),
    url(r'^task/(?P<task_id>[0-9]+)/document/(?P<document_id>[0-9]+)/sentences$', 
        views.document_sentences,
        name='document_sentences'),
    url(r'^task/(?P<task_id>[0-9]+)/document/add$', 
        views.document_add, 
        name='document_add'),
    url(r'^task/(?P<task_id>[0-9]+)/document/upload$', 
        views.document_upload, 
        name='document_upload'),
    url(r'^task/(?P<task_id>[0-9]+)/$', 
        views.task, 
        name='task'),
]

