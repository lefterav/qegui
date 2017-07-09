from django.test import TestCase
from django.urls import reverse

from .models import Task, Document, Sentence


def create_dummy_document():
    task = Task(name="Test task")
    task.save()
    document = Document(
                        name="Test document",
                        source_language="de",
                        target_language="en",
                        task=task,
                        )
    document.save()  
    return task, document


def create_dummy_sentence(text="Test sentence"):
    _, document = create_dummy_document()
    sentence = Sentence(
                                document=document,
                                text=text,
                                )
    sentence.save()
    return sentence


# Create your tests here.
class UrlTests(TestCase):
    def test_document_existing_task(self):
        """
        When task/task_id/document/document_id is given in the URL
        then the view should return results if the requested document
        is included in the requested task
        """
        task, document = create_dummy_document()
        
        response = self.client.get(reverse('qe:document', 
            kwargs={'task_id': task.id, 'document_id': document.id,})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['document'].id, document.id)
        
        
    def test_document_nonexisting_task(self):
        """
        When task/task_id/document/document_id is given in the URL
        then the view should return a 404 error if the requested 
        document is not included in the requested task
        """
        task, document = create_dummy_document()
        
        response = self.client.get(reverse('qe:document', 
            kwargs={'task_id': task.id+1, 'document_id': document.id,})
        )
        
        self.assertEqual(response.status_code, 404)
        
        
class SentenceTests(TestCase):
    def test_longsentence_chopping(self):
        """
        Make sure that the shortening of the sentence text for
        the string representation of the object works properly
        """
        longsentence = " ".join(["word"]*20)+" lastword"
        sentence = create_dummy_sentence(longsentence)
        
        sentence_id = int(str(sentence).split(":")[0])
        # get only the text (first comes the sentence id)
        string_representation = str(sentence).split(":")[1].strip()
        # it should have 19 times word + "..." + lastword = 22 words
        self.assertEqual(len(string_representation.split()), 20,
                         msg="The sentence chopper failed to \
                          reduce the length of the sentence text")
        self.assertEqual(string_representation, 
                         " ".join(["word"]*18)+" [...] lastword",
                         msg="The sentence chopper failed to \
                          reassemble a shorter sentence"),
        # make also sure that the sentence id is also there                 
        self.assertEqual(sentence_id, sentence.id)
        
        
    def test_shortsentence_chopping(self):
        """
        Make sure that the shorter sentences remain unshortened
        """
        shortsentence = " ".join(["word"]*19)+" lastword"
        sentence = create_dummy_sentence(shortsentence)
        string_representation = str(sentence).split(":")[1].strip()
        self.assertEqual(len(string_representation.split()), 20,
                         msg="The length of a short sentence is not \
                         maintained")
        self.assertFalse(("[...]" in string_representation),
                         msg="It is likely that the sentence chopper \
                         shortened a sentence that it shouldn't")     
        
        
        