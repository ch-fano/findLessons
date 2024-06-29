from django.shortcuts import render

# Create your views here.
def reservation_home(request):
    return render(request, 'reservation/home.html')