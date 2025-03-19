from django.db import models
import pandas as pd
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.
class Category1(models.Model):
    name1=models.CharField(max_length=35)
    
    class Meta:
        verbose_name_plural='Categories'

    def __str__(self):
        return self.name1
class Quiz1(models.Model):
    title1=models.CharField(max_length=255)
    description1=models.TextField()
    category1=models.ForeignKey(Category1,on_delete=models.CASCADE)
    quiz_fiel1=models.FileField(upload_to='quiz1/')
    created_at1=models.DateTimeField(auto_now_add=True)
    updated_at1=models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural='Quizes'

    def __str__(self):
        return self.title1    
    
    # call the function on quiz save
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.quiz_fiel1:
            self.import_quiz_from_excel()

    
    #function to extract file
    def import_quiz_from_excel(self):
        # read excel
        df = pd.read_excel(self.quiz_fiel1.path)

        #iterate over the each row
        for index,row in df.iterrows():
            # extract question,text and choices and correct ans from the row
            question_text = row['Question']
            choice1 = row['A']
            choice2 = row['B']
            choice3 = row['C']
            choice4 = row['D']
            correct_answer=row['Answer']

            #create the question object
            question = Question.objects.get_or_create(quiz=self,text=question_text)
            
            #create choice object
            choice_1=Choice.objects.get_or_create(question=question[0], text=choice1, is_correct=correct_answer == 'A')
            choice_2=Choice.objects.get_or_create(question=question[0], text=choice2, is_correct=correct_answer == 'B')
            choice_3=Choice.objects.get_or_create(question=question[0], text=choice3, is_correct=correct_answer == 'C')
            choice_4=Choice.objects.get_or_create(question=question[0], text=choice4, is_correct=correct_answer == 'D')
            
#questions and choice model
class Question(models.Model):
    quiz=models.ForeignKey(Quiz1,on_delete=models.CASCADE)
    text=models.TextField()
    
    def __str__(self):
        return self.text[:50]
    
class Choice(models.Model):
    question=models.ForeignKey(Question,on_delete=models.CASCADE)
    text=models.CharField(max_length=255)
    is_correct=models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.text[:50]}, {self.text[:20]}"
    

class QuizSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz= models.ForeignKey(Quiz1,on_delete=models.CASCADE)
    score = models.IntegerField()
    submitted_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}, {self.quiz.title1}"
    
class UserRank(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)  
    rank=models.IntegerField(null=True,blank=True)
    total_score=models.IntegerField(null=True,blank=True)

    def __str__(self):
        return f"{self.rank}, {self.user.username}"
#if any user submit the quiz call update leaderboard    
@receiver(post_save, sender=QuizSubmission)
def update_leaderboard(sender, instance, created, **kwargs):
    if created:
        update_leaderboard()
def update_leaderboard():
    # count the sum of scores for all user
    user_scores=(QuizSubmission.objects.values('user').annotate(total_score=Sum('score')).order_by('-total_score'))

    # update rank based on the sorted list
    rank = 1
    for entry in user_scores:
        user_id=entry['user']
        total_score=entry['total_score']

        user_rank, created = UserRank.objects.get_or_create(user_id=user_id)
        user_rank.rank = rank
        user_rank.total_score=total_score
        user_rank.save()

        rank+=1
