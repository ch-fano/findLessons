from django.shortcuts import render

def homepage(request):
    ctx = {'title':'findLessons'}
    return render(request, template_name='homepage.html', context=ctx)

