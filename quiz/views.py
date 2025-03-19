from django.shortcuts import render

#create you view
def all_quiz_view(request):

    context={}
    return render(request,'all-quiz.html',context)