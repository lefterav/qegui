from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.aggregates import Count
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls.base import reverse
from django.utils.translation import ugettext as _

from .charts import AverageScoreChart
from .charts import ScoreMassChart
from .models import Document, Task, MachineTranslationEvaluation
from .tasks import process_sentences


def index(request):
    """
    The initial dashboard view with a list of tasks
    """
    tasks = Task.objects.order_by('name') \
    .annotate(documents=Count('document')) \
    .annotate(total_sentences=Count('document__sentence'))    
    #tasks_table = TaskTable(tasks)
        
    return render(
                  request, 
                  'qe/index.html', 
                  {'tasks': tasks},
                  )
    

def task(request, task_id):
    """
    A view that lists the documents in the specified task
    """
    task = get_object_or_404(Task, pk=task_id)
    try:
        documents_list = Document.objects.filter(task=task_id) \
        .annotate(total_sentences=Count('sentence'))
    except:
        documents_list = []
    #documents_table = DocumentTable(documents_list)
        
    context = {
               'task': task,
               #'documents_table': documents_table,
               'documents': documents_list,
               }
    
    return render(request, 'qe/task.html', context)


def document(request, task_id, document_id):
    """
    A view that presents the results for the specified document
    """
    document = get_object_or_404(Document, pk=document_id, task__id=task_id)
    
    average_score = 0
    chart_html = ""
    average_score_chart_html = ""
    
    
    if not document.imported:
        messages.warning(
                         request, 
                         _("The sentences of this document are still being imported")
                         )
    elif not document.evaluated:
        messages.warning(
                         request, 
                         _("The sentences of this document are still being evaluated")
                        )
    else:
        chart = ScoreMassChart()
        chart_html = chart.as_html(document_id=document_id)
        
        
        
        # calculate average score
        scores = MachineTranslationEvaluation \
            .objects.filter(translation__source__document_id=document_id) \
            .values_list('score', flat=True)
        
        
        average_score = round((1.0 * sum(scores)) / len(scores), 2)
        
        average_score_chart = AverageScoreChart()
        average_score_chart_html = average_score_chart.as_html(average_score)
        
    context = {
               'document': document,
               'chart': chart_html,
               'average_score_chart': average_score_chart_html,
               'average_score': average_score,
               }
    
    return render(request, 'qe/document.html', context)


def document_add(request, task_id):
    """
    A form that allows uploading a new document 
    """
    task = get_object_or_404(Task, pk=task_id)
    context = {
               'task': task,
               'languages': settings.LANGUAGES,
               }
    
    return render(request, 'qe/document_add.html', context)


def document_upload(request, task_id):
    """
    Respons to the form for adding a new document
    It triggers the background process for adding the sentences
    in the database and evaluating them.
    """
    task_id = request.POST['task_id']
    task = get_object_or_404(Task, pk=task_id)


    document = Document(name=request.POST['name'],
                        description=request.POST['description'],
                        task=task,
                        source_language=request.POST['source_language'],
                        target_language=request.POST['target_language'],
                        sourcefile=request.FILES['sourcefile'],
                        targetfile=request.FILES['targetfile'],
                        )
    
    try:
        document.referencefile=request.FILES['referencefile']
    except:
        pass
    document.save()
    
    process_sentences(document.id)

    return HttpResponseRedirect(reverse('qe:document', 
                                        args=(document.task.id, 
                                              document.id)
                                        )
                                )
    
def document_sentences(request, task_id, document_id):
    evaluation_list = MachineTranslationEvaluation.objects.order_by('score')
    paginator = Paginator(evaluation_list, 10) # Show 10 evaluations per page_id
    document = get_object_or_404(Document, pk=document_id, task_id=task_id)
    
    page_id = request.GET.get('page')


    try:
        evaluations = paginator.page(page_id)
    except PageNotAnInteger:
        # If page_id is not an integer, deliver first page_id.
        evaluations = paginator.page(1)
    except EmptyPage:
        # If page_id is out of range (e.g. 9999), deliver last page_id of results.
        evaluations = paginator.page(paginator.num_pages)
    
    context = {'evaluations': evaluations,
               'document': document,
               'show_first': int(page_id)-3,
               'show_last': int(page_id)+3,
               'end_index': paginator.num_pages
                }
    return render(request, 'qe/document_sentences.html', context)
    
