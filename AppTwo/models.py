from django.db import models

# Create your models here.
class Article(models.Model):

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=120)
    url = models.TextField()
    pub_date = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=30)

    def __str__(self):
        return 'Article # %s with title: %s' % (str(self.id), self.title)
