from django.shortcuts import render, redirect, get_object_or_404
from .crawl import browser_on, href_crawler, image_scrapping
from .models import Post, Chart, Size
from darkflow.net.build import TFNet
from .tablefinder import crop_col_img, split_img, yolo_split, find_table, img_concat
import hashlib
import cv2
import os
from .textdetect import black_find_contour, white_find_contour, \
    split_row, category_row, text_recognition, find_column, text_check


# import os
# print(os.getcwd())

# YOLO MODEL LOAD
def load_yolo(load_weight):
    # model은 사용하는 cfg model
    options = {"model": "cfg/size-yolo.cfg",
               "load": load_weight}  # 최신 checkpoint를 load하려면 -1
    tfnet = TFNet(options)
    tfnet.load_from_ckpt()
    return tfnet


load_weight = 31333
tfnet = load_yolo(load_weight)


# Create your views here.


def index(request):
    return render(request, 'boards/index.html')


def service(request):
    query = request.GET.get('query')
    posts = Post.objects.filter(category=query)
    context = {
        'posts': posts,
        'query': query,
    }
    return render(request, 'boards/service.html', context)


def manage(request):
    query = request.GET.get('query')
    browser = browser_on()
    title_list, href_list, src_list, price_list = href_crawler(browser, query, 2)

    # 데이터베이스에 저장
    for (title, thumbnail, link, price) in zip(title_list, src_list, href_list, price_list):
        # DB에 있는지 확인
        if Post.objects.filter(title=title):
            print(f"{title} is already in db")
        else:
            # DB에 없다면 저장!
            post = Post()
            post.category = query
            post.title = title
            post.thumbnail = thumbnail
            post.link = link
            post.price = price
            post.save()

            href = [post.link]
            category = post.category
            hash_object = hashlib.sha1(f"{category}".encode('utf-8'))
            hex_dig = hash_object.hexdigest()
            filename = f"/boards/static/boards/images/screenshot/{hex_dig}_{post.id}.jpg"
            # saves screenshot, no return
            image_scrapping(href, filename, browser)
            img = crop_col_img(filename)
            split_imgs = split_img(img)
            split_imgs = img_concat(split_imgs)

            for idx, slice in enumerate(split_imgs):
                yolo_slice = yolo_split(slice, tfnet)
                if yolo_slice == 0:
                    continue
                tables = find_table(yolo_slice)
                if tables:
                    print(len(tables))
                    for idx2, table in enumerate(tables):
                        tablename = f"C:/STUDY/FindSizeProject/django_app/boards/static/boards/images/tables/" \
                            f"{hex_dig}_{post.id}_{idx}_{idx2}.jpg"
                        print(tablename)
                        print(type(table.img))
                        print(table.img)
                        print(table.img.shape)
                        cv2.imwrite(tablename, table.img)
                        _, tail = os.path.split(tablename)
                        relpath = 'boards/images/tables/' + tail
                        chart = Chart(post_id=post.id, img=relpath)
                        chart.save()

            print(f"{title} 저장!")

    datas = {}
    for (a, b, c, d) in zip(title_list, src_list, href_list, price_list):
        post = Post.objects.filter(title=a)[0]
        datas[a] = [b, c, d, post.id]
    context = {
        'datas': datas,
        'query': query,
    }

    browser.quit()
    return render(request, 'boards/manage.html', context)


def extract(request, post_pk):
    post = get_object_or_404(Post, id=post_pk)
    href = [post.link]
    # OpenCV won't take Korean as filename,
    # so HASHING it so it can.
    category = post.category
    hash_object = hashlib.sha1(f"{category}".encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    filename = f"/boards/static/boards/images/screenshot/{hex_dig}_{post.id}.jpg"
    # saves screenshot, no return
    browser = browser_on()
    image_scrapping(href, filename, browser)
    browser.quit()
    img = crop_col_img(filename)
    split_imgs = split_img(img)
    split_imgs = img_concat(split_imgs)

    for idx, slice in enumerate(split_imgs):
        yolo_slice = yolo_split(slice, tfnet)
        if yolo_slice == 0:
            continue
        tables = find_table(yolo_slice)
        if tables:
            print(len(tables))
            for idx2, table in enumerate(tables):
                tablename = f"C:/STUDY/FindSizeProject/django_app/boards/static/boards/images/tables/" \
                    f"{hex_dig}_{post.id}_{idx}_{idx2}.jpg"
                print(tablename)
                print(type(table.img))
                print(table.img)
                print(table.img.shape)
                cv2.imwrite(tablename, table.img)
                _, tail = os.path.split(tablename)
                relpath = 'boards/images/tables/' + tail
                chart = Chart(post_id=post.id, img=relpath)
                chart.save()

    # post.category = post.category
    # post.title = post.title
    # post.thumbnail = post.thumbnail
    # post.link = post.link
    # post.price = post.price
    #
    # post.save()
    return redirect('boards:index')


def detect(request):
    charts = Chart.objects.all()
    for chart in charts:
        img = os.getcwd() + '/boards/static/' + chart.img
        print(img)
        img = cv2.imread(img)

        table_img_list = [img]
        size_table = []
        for table in table_img_list:
            try:
                # 영역치고
                black_rect = black_find_contour(table)
                white_rect = white_find_contour(table)
                # 행으로 분리하고
                black_row = split_row(black_rect)
                white_row = split_row(white_rect)
                # 분리된 행 카테고리화 하고
                black_rows_list = category_row(black_row)
                white_rows_list = category_row(white_row)
                # 텍스트 인식하고
                black_text = text_recognition(black_rows_list)
                white_text = text_recognition(white_rows_list)
                # 체크 하고
                text = text_check(black_text, white_text)
                size_table.append(text)
            except Exception as e:
                print(f'error : {e}')
                continue

        print("tables : ", len(size_table))
        for table in size_table:
            print("SIZE EXIST? : ", table.size_bool)
            if table.size_bool:  # if True
                print("arm : ", table.arm_size)  # list
                print("shoulder : ", table.sh_size)  # list

                for arm in table.arm_size:
                    size = Size()
                    size.category = "arm"
                    size.size = arm
                    size.chart_id = chart.id
                    size.save()

                for shoulder in table.sh_size:
                    size = Size()
                    size.category = "shoulder"
                    size.size = shoulder
                    size.chart_id = chart.id
                    size.save()
            else:
                print("NO WAY JOSE")

    return render(request, 'boards/index.html')

