from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from Account.models import Profile
from .models import Quiz1,Category1
from django.db.models import Q
from quiz1.models import QuizSubmission
from django.contrib import messages
# Create your views here.

@login_required(login_url='login')
def all_quiz_view1(request):
   user_object=User.objects.get(username=request.user)
   user_profile=Profile.objects.get(user=user_object)
   
   quizes=Quiz1.objects.order_by("-created_at1")
   categories=Category1.objects.all()
   context={"user_profile":user_profile, "quizes":quizes,"categories":categories}
   return render(request, 'all-quiz.html', context)

#search bar view
@login_required(login_url='login')
def search_view(request,category):
   user_object=User.objects.get(username=request.user)
   user_profile=Profile.objects.get(user=user_object)
   #search by through search bar
   if request.GET.get('q') != None:
      q = request.GET.get('q')
      query=Q(title1__icontains=q) | Q(description1__icontains=q)
      quizes=Quiz1.objects.filter(query).order_by("-created_at1")
   # search by category 
   elif category!=" ":
      quizes=Quiz1.objects.filter(category1__name1=category).order_by("-created_at1")
   else:
      quizes=Quiz1.objects.order_by("-created_at1")
   categories=Category1.objects.all()
   context={"user_profile":user_profile, "quizes":quizes,"categories":categories}
   return render(request,'all-quiz.html',context)

#quiz view for questions
@login_required(login_url='login')
def quiz_view(request,quiz_id):
   user_object=User.objects.get(username=request.user)
   user_profile=Profile.objects.get(user=user_object)
   
   quiz=Quiz1.objects.filter(id=quiz_id).first()
   total_questions = quiz.question_set.all().count()
   if request.method=="POST":
      # get the score
      score = int(request.POST.get('score',0))

      # check if the user has already submitted the quiz
      if QuizSubmission.objects.filter(user=request.user,quiz=quiz).exists():
         messages.success(request,f"this time you got {score} out of {total_questions}")
         return redirect('quiz',quiz_id)
      # save the new quiz
      submission=QuizSubmission(user=request.user,quiz=quiz,score=score)
      submission.save()

      #show the result in messages
      messages.success(request,f"Quiz Submitted successfully and you got {score} out of {total_questions}")
      return redirect('quiz',quiz_id)

   if quiz != None :
      context={"user_profile":user_profile,"quiz":quiz}
   else:
      return redirect('all_quiz')
   return render(request,'quiz.html',context)

@login_required(login_url='login')
def quiz_result_view(request,submission_id):
   user_object=User.objects.get(username=request.user)
   user_profile=Profile.objects.get(user=user_object)
   submission=QuizSubmission.objects.get(pk=submission_id)
   context={"user_profile":user_profile, "submission":submission}
   return render(request,'quiz-result.html',context)