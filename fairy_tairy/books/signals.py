from django.db.models.signals import  post_delete, pre_save
from django.dispatch import receiver
from .models import Page

@receiver(post_delete, sender=Page)
def update_page_order(sender, instance, **kwargs):
    pages_to_update = Page.objects.filter(book=instance.book, order__gt=instance.order)
    for page in pages_to_update:
        page.order -= 1
        page.save()
    print("Page order updated after deletion.")


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