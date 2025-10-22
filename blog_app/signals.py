from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save
from django.utils.text import slugify
from django.core.cache import cache
from django_redis import get_redis_connection

from blog_app.models import CategoryBlog, PostBlog


@receiver([post_save, post_delete], sender=CategoryBlog)
def invalidate_category_cache(sender, instance, **kwargs):
    redis_connection = get_redis_connection('default')
    key_list = redis_connection.keys("*category_list_cache*")
    retrieve_key = redis_connection.keys("*category_retrieve_cache*")
    if key_list:
        redis_connection.delete(*key_list)
    if retrieve_key:
        redis_connection.delete(*retrieve_key)


@receiver(pre_save, sender=CategoryBlog)
def create_category_slug(sender, instance, **kwargs):
    instance.category_slug = slugify(instance.category_name, allow_unicode=True)


@receiver([post_save, post_delete], sender=PostBlog)
def clear_cache_after_save(sender, instance, **kwargs):
    cache.delete("seo_blog_list_response")
