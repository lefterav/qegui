from django.contrib import admin


from .models import System, Task, Document, Sentence, MachineTranslation, ReferenceTranslation, DocumentEvaluation, MachineTranslationEvaluation

admin.site.register(System)
admin.site.register(Task)
admin.site.register(Document)
admin.site.register(MachineTranslationEvaluation)
admin.site.register(DocumentEvaluation)


class MachineTranslationInline(admin.StackedInline):
    model = MachineTranslation
    extra = 1

class ReferenceTranslationInline(admin.StackedInline):
    model = ReferenceTranslation
    extra = 1


class SentenceSentenceAdmin(admin.ModelAdmin):
    """
    allows inline editing of MT ouputs and references for every 
    source sentence
    """
    inlines = [
        MachineTranslationInline,
        ReferenceTranslationInline,
    ]

admin.site.register(Sentence, SentenceSentenceAdmin)
