from django.test import TestCase
from .models import Quiz1,QuizSubmission,Category1,Choice
import pandas as pd
import io
from django.core.files.uploadedfile import SimpleUploadedFile
class QuizModelTest(TestCase):
    def setUp(self):
        self.catogory=Category1.objects.create(name1='Coding')
        
        #create xl file
        self.excel_file=io.BytesIO()
        df=pd.DataFrame({
            'Question':['What is 2+2?','What is 3+5?'],
            'A':['1','2'],
            'B':['3','4'],
            'C':['5','8'],
            'D':['4','9'],
            'Answer':['D','C'],
        })
        df.to_excel(self.excel_file, index=False)

        self.uploaded_file = SimpleUploadedFile('test_quiz.xlxs',self.excel_file.read(), content_type='application/vnd.ms-excel')
        #quiz
        self.quiz=Quiz1.objects.create(
            title1="Quiz title",
            description1="Quiz description1",
            category1=self.catogory,
            quiz_fiel1=self.uploaded_files,

        )
    @patch('')
    def test_import_quiz_from_excel(self):
        df=pd.DataFrame({
            'Question':['What is 2+2?','What is 3+5?'],
            'A':['1','2'],
            'B':['3','4'],
            'C':['5','8'],
            'D':['4','9'],
            'Answer':['D','C'],
        })
