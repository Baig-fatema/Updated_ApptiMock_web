from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from Account.models import Profile
from quiz1.models import UserRank,QuizSubmission,Question,Quiz1
from django.contrib.auth.decorators import login_required, user_passes_test
import datetime
import math
from .models import Message,Blog
from django.db.models import Count,Q
from django.contrib import messages
from django.db.models.functions import ExtractYear
#chatbot 

import openai
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Load API key securely
openai.api_key = os.getenv("OPENAI_API_KEY")

@csrf_exempt
def chatbot_response(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message")

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # or "gpt-4" if you have access
                messages=[{"role": "system", "content": "You are a helpful assistant."},
                          {"role": "user", "content": user_message}]
            )

            bot_reply = response["choices"][0]["message"]["content"]
            return JsonResponse({"reply": bot_reply})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)


# Create your views here.
def home(request):

    leaderboard_users=UserRank.objects.order_by('rank')[:4]
    #request user
    #second user (if you are seeing others profile than )
    if request.user.is_authenticated:
        user_object=User.objects.get(username=request.user)
        user_profile=Profile.objects.get(user=user_object)
        context={'user_profile':user_profile,"leaderboard_users":leaderboard_users}
    else:
        context={"leaderboard_users":leaderboard_users} 
    return render(request,'welcome.html',context)

@login_required(login_url='login')
def leaderboard_view(request):
    user_object=User.objects.get(username=request.user)
    user_profile=Profile.objects.get(user=user_object)
    
    leaderboard_users=UserRank.objects.order_by('rank')
    
    context={"leaderboard_users":leaderboard_users,'user_profile':user_profile}
    return render(request,'leaderboard.html',context)

def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
@login_required(login_url='login')
def dashboard_view(request):
    user_object=User.objects.get(username=request.user)
    user_profile=Profile.objects.get(user=user_object)
    # total numbers
    total_users=User.objects.all().count()
    total_quizes=Quiz1.objects.all().count()
    total_quiz_submit=QuizSubmission.objects.all().count()
    total_questions=Question.objects.all().count()
    #today numbers 
    today_users = User.objects.filter(date_joined__date=datetime.date.today()).count()
    today_quizzes = Quiz1.objects.filter(created_at1=datetime.date.today()).count()
    today_quizzes_objs = Quiz1.objects.filter(created_at1__date=datetime.date.today())
    today_quiz_submit = QuizSubmission.objects.filter(submitted_at__date=datetime.date.today()).count()
    today_questions = 0
    for quiz in today_quizzes_objs:
        today_questions +=quiz.question_set.count()
    gain_users=gain_percentage(total_users,today_users)
    gain_quizzes=gain_percentage(total_quizes,today_quizzes)
    gain_quiz_submit=gain_percentage(total_quiz_submit,today_quiz_submit)
    gain_questions=gain_percentage(total_questions,today_questions)
    
    #inbox messages
    messages=Message.objects.filter(created_at__date=datetime.date.today()).order_by('-created_at')


    context={"user_profile":user_profile,
             "total_users":total_users,
             "total_quizes":total_quizes,
             "total_quiz_submit":total_quiz_submit,
             "total_questions":total_questions,
             "today_users":today_users,
             "today_quizzes":today_quizzes,
             "today_quiz_submit":today_quiz_submit,
             "today_questions":today_questions,
             "gain_users":gain_users,
             "gain_quizzes":gain_quizzes,
             "gain_quiz_submit":gain_quiz_submit,
             "gain_questions":gain_questions,
             "messages":messages,
             }
    return render(request,"Dashboard.html",context)

def gain_percentage(total,today):
    if total>0 and today>0:
        gain = math.floor((today * 100)/total)
        return gain

def about_view(request) :
    if request.user.is_authenticated:
        user_object=User.objects.get(username=request.user)
        user_profile=Profile.objects.get(user=user_object)
        context={"user_profile":user_profile}
    else:
        context={}
    return render(request,"Aboutus.html",context)

def blogs_view(request) :
    #unique year for blogs
    year_blog_count=Blog.objects.annotate(year=ExtractYear('created_at')).values('year').annotate(count=Count('id')).order_by('-year').filter(status='public')
    
    blogs=Blog.objects.filter(status='public').order_by('-created_at')

    
    if request.user.is_authenticated:
        user_object=User.objects.get(username=request.user)
        user_profile=Profile.objects.get(user=user_object)
        context={"user_profile":user_profile,"year_blog_count":year_blog_count,"blogs":blogs}
    else:
        context={"year_blog_count":year_blog_count,"blogs":blogs}
    return render(request,"Blogs.html",context)

#each blog
@login_required(login_url='login')
def blog_view(request,blog_id) :
        user_object=User.objects.get(username=request.user)
        user_profile=Profile.objects.get(user=user_object)
        
        blog=Blog.objects.filter(id=blog_id).first()

        context={"user_profile":user_profile,"blog":blog}
        return render(request,"blog.html",context)

@login_required(login_url='login')
def contact_view(request):
        user_object=User.objects.get(username=request.user)
        user_profile=Profile.objects.get(user=user_object)
        if request.method == "POST":
             subject =  request.POST.get('subject')
             message =  request.POST.get('message')

             if subject is not None and message is not None:
                  form = Message.objects.create(user=request.user, subject=subject, message=message)
                  form.save()
                  messages.success(request, "We got your message. we will resolve your query soon. ")
                  return redirect('profile',request.user.username)
             else:
                  return redirect('contact')
             
        context={"user_profile":user_profile}
        return render(request,"contact.html",context)

@user_passes_test(is_superuser)
@login_required(login_url='login')
def message_view(request, id):
    user_object=User.objects.get(username=request.user)
    user_profile=Profile.objects.get(user=user_object)

    message=Message.objects.filter(id=int(id)).first()
    if not message.is_read:
         message.is_read=True
         message.save()
    
    context={"user_profile":user_profile,"message":message}
    return render(request,'message.html',context)

def conditions_view(request):
    if request.user.is_authenticated:
        user_object=User.objects.get(username=request.user)
        user_profile=Profile.objects.get(user=user_object)
        context={"user_profile":user_profile}
    else:
        context={}
    return render(request,"Terms&conditions.html",context)
        
@login_required(login_url='login')
def download_view(request) :
        user_object=User.objects.get(username=request.user)
        user_profile=Profile.objects.get(user=user_object)
        context={"user_profile":user_profile}
        return render(request,"Download.html",context)

#search bar on navbar
def search_users_view(request):
    query=request.GET.get('q')

    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        ).order_by('date_joined')
    else:
        users = []
    
    if request.user.is_authenticated:
        user_object=User.objects.get(username=request.user)
        user_profile=Profile.objects.get(user=user_object)
        context={"user_profile":user_profile,"query":query,"users":users}
    else:
        context={"query":query,"users":users}
    return render(request,"search_users.html",context)
    
def custom_404(request,exception):
     render(request,'404.html',status=404)  
