'''
@author: lefterav
'''
from django_tables2.utils import A  # alias for Accessor
import django_tables2 as tables
from .models import Task, Document

class TaskTable(tables.Table):
    name = tables.LinkColumn('qe:task', args=[A('pk')])

    class Meta:
        model = Task
        attrs = {'class': 'table table-hover table-responsive'}
        fields = ('id', 'name', 'description', 
                  'documents', 'total_sentences')


class DocumentTable(tables.Table):

    name = tables.LinkColumn('qe:document', 
                             args=[A('task.pk'), A('pk')])
        
    class Meta:
        model = Document 
        attrs = {'class': 'table-striped'}
        fields = ('id', 'name', 'description', 
                  'total_sentences', 'source_language', 
                  'target_language')
