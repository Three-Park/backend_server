from django.db import models
from django.conf import settings
from diaries.models import Diary
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

# Create your models here.

class Book(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book_title = models.CharField(max_length = 30)
    author = models.CharField(max_length = 30)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_open = models.BooleanField(default=False)
    
    class Meta: 
        managed = True
        db_table = 'book'


class Page(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book=models.ForeignKey(Book, on_delete=models.CASCADE)
    diary=models.ForeignKey(Diary, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)
    
    class Meta:
        unique_together = ('book', 'diary')
        ordering = ['order']  # 순서대로 정렬
        managed = True
        db_table='page'
        
    def save(self, *args, **kwargs):
        if not self.order:
            # 새 페이지에 대한 순서를 설정합니다.
            last_page = Page.objects.filter(book=self.book, diary=self.diary).order_by('-order').first()
            if last_page:
                self.order = last_page.order + 1
            else:
                self.order = 1
        super(Page, self).save(*args, **kwargs)
        
@receiver(pre_save, sender=Page)
def set_page_order(sender, instance, **kwargs):
    if not instance.order:
        # 새 페이지에 대한 순서를 설정합니다.
        last_page = Page.objects.filter(book=instance.book).order_by('-order').first()
        print('ordering...')
        if last_page:
            instance.order = last_page.order + 1
        else:
            instance.order = 1
            
@receiver(post_delete, sender=Page)
def update_page_order(sender, instance, **kwargs):
    # 페이지를 삭제한 후에는 순서를 업데이트합니다.
    pages_to_update = Page.objects.filter(book=instance.book, order__gt=instance.order)
    for page in pages_to_update:
        page.order -= 1
        page.save()