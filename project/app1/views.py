from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.db.models import Q
from .models import Member


def members(request):
    query = request.GET.get('q', '').strip()
    all_members = Member.objects.all().order_by('id')

    if query:
        all_members = all_members.filter(
            Q(firstname__icontains=query) | Q(lastname__icontains=query)
        )

    template = loader.get_template('members.html')
    context = {
        'members': all_members,
        'query': query,
    }
    return HttpResponse(template.render(context, request))


def add_member(request):
    if request.method == 'POST':
        Member.objects.create(
            firstname=request.POST.get('firstname', '').strip(),
            lastname=request.POST.get('lastname', '').strip(),
            phone=request.POST.get('phone') or None,
            joined_date=request.POST.get('joined_date') or None,
        )
        return redirect('members')

    template = loader.get_template('add_member.html')
    return HttpResponse(template.render({}, request))


def update_member(request, id):
    member = get_object_or_404(Member, id=id)
    # member = Member.objects.get(id=id)
    if request.method == 'POST':
        member.firstname = request.POST.get('firstname', '').strip()
        member.lastname = request.POST.get('lastname', '').strip()
        member.phone = request.POST.get('phone') or None
        member.joined_date = request.POST.get('joined_date') or None
        member.save()
        return redirect('members')

    template = loader.get_template('update_member.html')
    context = {
        'member': member,
    }
    return HttpResponse(template.render(context, request))


def delete_member(request, id):
    member = get_object_or_404(Member, id=id)

    if request.method == 'POST':
        member.delete()
        return redirect('members')

    template = loader.get_template('delete_member.html')
    context = {
        'member': member,
    }
    return HttpResponse(template.render(context, request))
