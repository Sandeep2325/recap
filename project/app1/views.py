from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
def members(request):
    members=Members.objects.all().values()
    template = loader.get_template('first.html')
    return HttpResponse(template.render())
# Create your views here.
