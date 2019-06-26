HEROKU에 웹 deploy

1. 웹어플이 github에 올라가게 해줌
2. gitignore에 추가

# Text backup files
*.bak

# Database
*.sqlite3

# 환경 설정 관련 파일
.env

3. 환경변수 관리

pip install python-decouple

.env 파일 생성
>>> 내용 추가
SECRET_KEY=settings.py에 있는 값 그대로 넣어주기
DEBUG=False

settings.py 수정
>>> from decouple import config
>>> SECRET_KEY = config('SECRET_KEY')
>>> DEBUG = config('DEBUG')

django 앱deploy 체크
>>> python manage.py check --deploy

django heroku 설치
>>> pip install django-heroku

settings.py 수정 (맨 밑에 추가)
>>> import django_heroku
>>> django_heroku.settings(locals())

프로젝트 경로에 파일 추가
Procfile 파일 생성
내용 추가
>>> web: gunicorn main.wsgi --log-file -
** gunicorn이란? **
Heroku, Django와 연동하는 HTTP 전용 서버

runtime.txt 파일 생성
터미널에서 python -V 으로 파이썬 버전 확인.
그 값을 파일 내용에 추가
>>> python-3.6.7

heroku 계정 생성

https://devcenter.heroku.com/articles/heroku-cli 로 접속

heroku 어플 installer 다운로드 및 설치
pycharm 껏다 키고 난후 터미널에서 다음 명령어 실행
>>> heroku
뭐가 떳으면 잘 설치된거임.

로그인
>>> heroku login
웹브라우저로 로그인화면 뜸. 로그인할것.

heroku 앱 생성 (csppl라는 이름으로)
>>> heroku create csppl

