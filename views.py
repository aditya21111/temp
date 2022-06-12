import tutorial
from django.http.response import Http404, HttpResponse
from django.shortcuts import redirect, render,HttpResponse
from blog.models import post
from tutorial.models import Tutorials
from rest_framework.decorators import api_view
from rest_framework.response import Response
from blog.serializers import postserilizer
from tutorial.serializers import Tutorialsserilizer
from django.core.paginator import Paginator
from .models import feedback
from .serializers import feedbackserilizer
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from rest_framework import status


import os

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
error_404=never_cache(TemplateView.as_view(template_name='index.html'))
error_400=never_cache(TemplateView.as_view(template_name='index.html'))
home=never_cache(TemplateView.as_view(template_name='index.html'))
blog=never_cache(TemplateView.as_view(template_name='index.html'))
blogpost=never_cache(TemplateView.as_view(template_name='index.html'))
tutorial=never_cache(TemplateView.as_view(template_name='index.html'))
tutorials_post=never_cache(TemplateView.as_view(template_name='index.html'))
search=never_cache(TemplateView.as_view(template_name='index.html'))
tut_post_desc=never_cache(TemplateView.as_view(template_name='index.html'))
def about(request):
    return HttpResponse("about page")



def policy(request):
    return render(request,'policy.html')


@api_view(['GET'])
def apisearch(request):


    query=request.query_params['query']
    print(query)

    if len(query)  > 80:
        posts=post.objects.none()
        return Response({'status': 'details'}, status=status.HTTP_404_NOT_FOUND)
    else:
        post_titlesearch=post.objects.filter(title__icontains=query,tutorial=False)
        post_contentsearch=post.objects.filter(content__icontains=query,tutorial=False)
        tut_titlesearch=post.objects.filter(title__icontains=query,tutorial=True)
        tut_contentsearch=post.objects.filter(content__icontains=query,tutorial=True)
        post_srch=post_titlesearch.union(post_contentsearch)

        tut_srch=tut_titlesearch.union(tut_contentsearch)
        posts=post_srch.union(tut_srch)

        paginator = Paginator(posts, 10) # Show 10
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        serilizer=postserilizer(page_obj,many=True)



            # union -for merging query sets

        if posts.count() == 0 :
            return Response("Please enter suitable keywords")
        else:
            return Response(serilizer.data)





@api_view(['POST'])
def feedback(request):
    serializer=feedbackserilizer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

        # try:
        #     subject, from_email, to = 'Thank you', 'writerhubhere@gmail.com', email
        #     text_content = ""
        #     html_content = f'Hey <strong>{name}</strong>\n Thank you for contacting us\n We have received your enquiry and will respond you within 24 hours. For urgent enquiries please call us on one of the number below\n +91 some number'
        #     msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        #     msg.attach_alternative(html_content, "text/html")
        #     msg.send()
        # except Exception as e:
        #     messages.error(request,"Sorry we are not available right now.Try after 1 hour")





@csrf_exempt
def upload_image(request):
    if request.method == "POST":
        file_obj = request.FILES['file']
        file_name_suffix = file_obj.name.split(".")[-1]
        if file_name_suffix not in ["jpg", "png", "gif", "jpeg", ]:
            return JsonResponse({"message": "Wrong file format"})

        path = os.path.join(
            settings.MEDIA_ROOT,
            'tinymce',
        )
        # If there is no such path, create
        if not os.path.exists(path):
            os.makedirs(path)

        file_path = os.path.join(path, file_obj.name)

        file_url = f'{settings.MEDIA_URL}tinymce/{file_obj.name}'

        if os.path.exists(file_path):
            return JsonResponse({
                "message": "file already exist",
                'location': file_url
            })

        with open(file_path, 'wb+') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)

        return JsonResponse({
            'message': 'Image uploaded successfully',
            'location': file_url
        })
    return JsonResponse({'detail': "Wrong request"})