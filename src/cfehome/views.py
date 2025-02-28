import pathlib
from django.http import HttpResponse
from django.shortcuts import render

from visits.models import PageVisit

this_dir = pathlib.Path(__file__).resolve().parent

def home_page_view(request, *args, **kwargs):
    qs = PageVisit.objects.all()
    page_qs = PageVisit.objects.filter(path=request.path)
    my_title = "Homepage"
    my_context = {
        "my_title": my_title,
        "page_visit_count": page_qs.count(),
        "total_visit_count": qs.count(),
        "percent": page_qs.count() / qs.count() * 100

    }
    
    html_template = "home.html"
    PageVisit.objects.create(path = request.path)

    return render(request, html_template, my_context)