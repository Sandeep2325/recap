from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Member
def members(request):
    members=Member.objects.all().values()
    template = loader.get_template('first.html')
    context = {
        'members': members,
    }
    return HttpResponse(template.render(context, request))
# Create your views here.
