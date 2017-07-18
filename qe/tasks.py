'''
@author: lefterav
'''
import random

from background_task import background

from .models import Document, Sentence, MachineTranslation 
from .models import DocumentEvaluation
from .models import MachineTranslationEvaluation
from .models import ReferenceTranslation

#uncomment and change PYTHONPATH to get into production mode
#from qualitative import evaluate

@background
def process_sentences(document_id):
    read_sentences_from_files(document_id)
    evaluate_sentences(document_id)

def read_sentences_from_files(document_id):
    """
    Read sentences from uploaded files into sentence fields
    """
    document = Document.objects.get(pk=document_id)
    
    sourcefile = document.sourcefile
    targetfile = document.targetfile
    
    # proceed with importing only if document has not been
    # imported before
    if document.imported:
        return
    
    sourcefile.open()
    targetfile.open()
    try:
        referencefile = document.referencefile
        referencefile.open()
        has_reference = True
    except:
        has_reference = False
    
    # iterate for all source files
    for source_string in sourcefile:            
        
        # create a Sentence object for every source sentence
        parallelsentence = Sentence(text=source_string,
                                            document=document)
        parallelsentence.save()
        
        # for every source sentence there should be one translation
        # read it
        target_string = targetfile.readline()
        translation = MachineTranslation(text=target_string,
                                         source=parallelsentence)
        translation.save()
        
        # reference is optional, so check whether it exists
        if has_reference:
            reference_string = referencefile.readline()
            reference = ReferenceTranslation(text=reference_string,
                                             source=parallelsentence)
            reference.save()
    # let the document know that everything has been imported
    document.imported = True
    document.save()
    sourcefile.close()
    targetfile.close()
    if has_reference:
        referencefile.close()
        

def evaluate_sentences(document_id):
    """
    Produce one evaluation score per sentence
    """

    document = Document.objects.get(pk=document_id)
    while not document.imported:
        pass
    if document.evaluated:
        return
    # get all the sentences of the current document
#    models = QEModel.objects.all()
#    for model in models:
    sentences = Sentence.objects.filter(document=document)
    evaluation = DocumentEvaluation(document=document)
    evaluation.save()
    for sentence in sentences:
        translation = MachineTranslation.objects.get(source=sentence)
        translation_evaluation = \
            MachineTranslationEvaluation(
                                         translation=translation,
                                         evaluation=evaluation,
                                         # Uncomment to get into production mode
                                         #score=evaluate(sentence.text, translation.text)
                                         # Demo mode, get a random number
                                         score=0.01*random.randrange(000,100)
                                        )
        translation_evaluation.save()
    document.evaluated = True;
    document.save()
    
    
    
                                        
     
