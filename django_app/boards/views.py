from django.shortcuts import render, redirect
from .crawl import browser_on, href_crawler, image_scrapping, img_download
from .models import Post
from darkflow.net.build import TFNet

# import os
# print(os.getcwd())

# YOLO MODEL LOAD
options = {"model": "cfg/size-yolo.cfg",
           "load": 22000}  # 최신 checkpoint를 load하려면 -1
tfnet = TFNet(options)
tfnet.load_from_ckpt()


# Create your views here.


def index(request):
    return render(request, 'boards/index.html')


def service(request):
    query = request.GET.get('query')
    posts =  Post.objects.filter(category=query)
    context = {
        'posts': posts,
        'query': query,
    }
    return render(request, 'boards/service.html', context)


def manage(request):
    query = request.GET.get('query')
    browser = browser_on()
    title_list, href_list, src_list, price_list = href_crawler(browser, query, 1)

    # 데이터베이스에 저장
    for (title, thumbnail, link, price) in zip(title_list, src_list, href_list, price_list):
        post = Post()
        if Post.objects.filter(title=title):
            print(f"{title} is already in db")
        else:
            post.category = query
            post.title = title
            post.thumbnail = thumbnail
            post.link = link
            post.price = price
            post.save()
            print(f"{title} 저장!")

    datas = {}
    for (a, b, c, d) in zip(title_list, src_list, href_list, price_list):
        datas[a] = [b, c, d]
    context = {
        'datas': datas,
        'query': query,
    }
    return render(request, 'boards/manage.html', context)
