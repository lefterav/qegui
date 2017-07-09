from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _
from django_tables2.utils import A  # alias for Accessor


MT_TYPE = (
    (u'1', u'phrase-based SMT'),
    (u'2', u'hierarchical SMT'),
    (u'3', u'factored SMT'),
    (u'4', u'rule-based'),
    (u'5', u'template-based'),
    (u'6', u'neural MT'),
    (u'7', u'other'), 
)


class System(models.Model):
    """
    is a machine translation system that has been used to produce 
    translations
    """
    name = models.CharField(
        max_length=200,
        help_text=_('The name of the machine translation system',)
    )
    type = models.CharField(
        max_length=1,
        help_text='''The type of machine translation technology 
        that this system employs''',
        choices=MT_TYPE,
    )
    
    def __str__(self):
        return self.name


class Task(models.Model):
    """
    is a grouping for the evaluation of one or more documents
    """
    name = models.CharField(
        max_length=200,
        help_text=_('The name of the Task')
    )
    description = models.TextField(
        blank=True,
        help_text=_('A short description of the Task')
    )
    
    def __str__(self):
        return self.name
    

class Document(models.Model):
    """
    is a collection of translated sentences to be evaluated. 
    All sentences should have the same source and the same target 
    sentence.
    """
    name = models.CharField(
        max_length=200, 
        help_text=_('The name of the document')
    )
    description = models.TextField(
        blank=True,
        help_text=_('A short description of the origin and the contents of the document')
    )
    source_language = models.CharField(
        max_length=7, 
        choices=settings.LANGUAGES,
        help_text=_("The language of the original document")        
    )
    target_language = models.CharField(
        max_length=7, 
        choices=settings.LANGUAGES,
        help_text=_("The language that this document has been translated into")
    )
    task = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE,
        help_text='The Task that this Document belongs to',
    )
    sourcefile = models.FileField(
        upload_to='files/dataset/sources',
        help_text=_("Text file with one source sentence per line")
    )
    targetfile = models.FileField(
        upload_to='files/dataset/target',
        help_text=_("""Text file with one machine translation output per line,
        following the order of the source sentences in the source file""")
    )
    referencefile = models.FileField(
        upload_to='files/dataset/references',
        blank=True,
        null=True,
        help_text=_("""Optional text file with one reference translation 
        per line, following the order of the source sentences in the 
        source file""")
    )
    imported = models.BooleanField(
        default=False,
        help_text=_("Specifies if all sentences have been imported from the files")
    )
    evaluated = models.BooleanField(
        default=False,
        help_text=_("Specifies if all sentences have been evaluated")
    )
    
    def __str__(self):
        return self.name

# the following models should replace single fields
# in order to allow multiple translations per source
# TODO: update the document_add view to support multiple
# translation files
class MachineTranslationFile(models.Model):
    document = models.ForeignKey(Document,
                                 on_delete=models.CASCADE)
    system = models.ForeignKey(System)
    targetfile = models.FileField(
        upload_to='files/dataset/target',
    )
    
class ReferenceTranslationFile(models.Model):
    document = models.ForeignKey(Document,
                                 on_delete=models.CASCADE)    
    referencefile = models.FileField(
    )


@python_2_unicode_compatible
class AbstractSentence(models.Model):
    text = models.TextField()

    def chop(self, string, limit_words=20):
        """
        Produce a shortened version of the string, so as to fit in
        listings etc.
        """
        tokens = string.split()
        if len(tokens) > limit_words:
            return "{} [...] {}".format(" ".join(tokens[:limit_words-2]), 
                                        tokens[-1])
        return string
    
    def __str__(self):
        """
        The string representation of the sentence should contain the 
        index key of the object and a short representation of the string
        """
        return "{}: {}".format(self.pk, self.chop(self.text))
    
    class Meta:
        abstract = True


@python_2_unicode_compatible
class Sentence(AbstractSentence):
    """
    contains the text of the original sentence to be translated
    """
    document = models.ForeignKey(Document, 
        on_delete=models.CASCADE,
        help_text="The document that this sentence belongs to"
    )
    
    def get_source_language(self):
        return self.document.source_language
    
    def get_target_language(self):
        return self.document.target_language


@python_2_unicode_compatible
class MachineTranslation(AbstractSentence):
    """
    includes a machine translation output for a given source sentence
    """
    source = models.ForeignKey(Sentence, 
                               on_delete=models.CASCADE)
    system = models.ForeignKey(
        System, 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="""The machine translation system  
        that produced this sentence"""
    )


@python_2_unicode_compatible
class ReferenceTranslation(AbstractSentence):
    """
    includes a reference translation for a given source sentence
    """
    source = models.ForeignKey(Sentence)
    translator = models.CharField(
        max_length=200,
        help_text='''The name or id of the translator 
        that produced this reference''',
        blank=True)


QE_TYPE = (
    (u'1', u'continuous'),
    (u'2', u'binary'),
    (u'3', u'ranking'),
)

class QEModel(models.Model):
    """
    contains a trained quality estimation model
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True,)
    type = models.CharField(
        max_length=1, 
        choices=QE_TYPE,
        help_text='''The type of Quality Estimation tasks 
        that this model is capable of'''
        )
    #model = JSONField(
    #    load_kwargs={'object_pairs_hook': OrderedDict},
    model = models.FileField(upload_to='files/models')
    
    def __str__(self):
        return self.name


class DocumentEvaluation(models.Model):
    """
    organizes the evaluations of a document by a specific method
    """
    model = models.ForeignKey(
        QEModel,
        help_text=_("The model to be applied for the evaluation "),
        null=True,
        blank=True,
    )
    document = models.ForeignKey(
        Document,
        help_text=_("The document which is being evaluated"),
        on_delete=models.CASCADE,
    )


class MachineTranslationEvaluation(models.Model):
    """
    associates a score to a machine translation output
    """
    translation = models.ForeignKey(
        MachineTranslation,                        
        on_delete=models.CASCADE,
        help_text=_("The MT output that this evaluation refers to"),
    )
    evaluation = models.ForeignKey(
        DocumentEvaluation,
        on_delete=models.CASCADE,
        help_text=_("The evaluation set that this evaluation belongs to")
    )
    score = models.FloatField() 