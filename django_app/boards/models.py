from django.db import models


# Create your models here.


class Post(models.Model):
    category = models.TextField()
    title = models.TextField()
    link = models.TextField()
    thumbnail = models.TextField()  # 해당 필드에 null값이 들어가도 된다
    price = models.TextField()
    # chart = models.ImageField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id}. {self.title}'


class Chart(models.Model):
    img = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
