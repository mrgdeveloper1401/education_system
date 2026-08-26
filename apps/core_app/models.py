from hashlib import sha1

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from base.utils.validators import file_upload_validator
from apps.core_app.managers import PublishManager


def validate_image_size(value):
    max_size = 1
    if value.size > max_size * 1024 * 1024:
        # TODO, customize exception
        raise ValidationError(_("حداکثر حجم عکس 1 مگابایت باشد"))
    return value


class CreateMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class UpdateMixin(models.Model):
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    deleted_at = models.DateTimeField(null=True, editable=False)
    is_deleted = models.BooleanField(editable=False, null=True)

    objects = PublishManager()

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save()

    class Meta:
        abstract = True


class SitemapEntry(CreateMixin, SoftDeleteMixin):
    slug_text = models.TextField()
    last_modified = models.CharField(blank=True)
    changefreq = models.CharField(
        max_length=255,
    )
    priority = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.5,
        help_text='A value between 0.00 and 1.00'
    )

    class Meta:
        db_table = "site_map"


class CourseSiteInformation(CreateMixin, UpdateMixin, SoftDeleteMixin):
    user_counter = models.CharField(max_length=10, blank=True)
    task_counter = models.CharField(max_length=10, blank=True)
    class_counter = models.CharField(max_length=10)
    video_counter = models.CharField(max_length=10, blank=True)

    class Meta:
        db_table = 'course_site_information'

class Image(CreateMixin, UpdateMixin, SoftDeleteMixin):
    title = models.CharField(max_length=128, null=True, blank=True)
    image = models.ImageField(width_field="width", height_field="height", upload_to="images/%Y/%m/%d",
                              validators=(validate_image_size,),
                              help_text=_("max size is 1 MG"))
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    file_hash = models.CharField(max_length=40, null=True, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True, help_text=_("file size as xx.b"))
    image_address = models.URLField(null=True, blank=True)

    @property
    def generate_hash(self):
        hasher = sha1()
        for c in self.image.chunks():
            hasher.update(c)
        return hasher.hexdigest()

    def __str__(self):
        return f"{self.file_hash} && {self.title}"

    @property
    def image_url(self):
        return self.image.url if self.image else None

    def save(self, *args, **kwargs):
        self.file_hash = self.generate_hash
        self.file_size = self.image.size
        self.image_address = self.image.url
        return super().save(*args, **kwargs)

    class Meta:
        db_table = "image"
        verbose_name = _("Image")
        verbose_name_plural = _("Images")
        ordering = ('-created_at',)


class State(models.Model):
    state_name = models.CharField(_("استان"), max_length=30, unique=True)

    def __str__(self):
        return self.state_name

    class Meta:
        ordering = ("state_name",)
        db_table = "state"
        verbose_name = _("استان")
        verbose_name_plural = _("استان ها")


class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name="cites", verbose_name=_("استان"))
    city = models.CharField(_("شهر"), max_length=40, db_index=True)

    def __str__(self):
        return self.city

    class Meta:
        ordering = ("-id",)
        db_table = "city"
        verbose_name = _("شهر")
        verbose_name_plural = _("شهر ها")
        unique_together = [('state', "city")]

class Banner(CreateMixin, UpdateMixin, SoftDeleteMixin):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='banners/%Y/%m/%d')
    is_publish = models.BooleanField(default=True)
    banner_type = models.CharField(
        choices=(("coach", "coach"), ("student", "student"), ("public", "public")),
        max_length=7,
        help_text="Banner type",
    )

    class Meta:
        db_table = 'banner'
        ordering = ('-created_at',)


class HeaderSite(CreateMixin, UpdateMixin, SoftDeleteMixin):
    header_title = models.CharField(max_length=50, help_text="عنوان هدر", blank=True, null=True)
    image = models.ImageField(upload_to="header_title/%Y/%m/%d", validators=[file_upload_validator],
                              blank=True, null=True)
    is_publish = models.BooleanField(default=True)
    text_color = models.CharField(max_length=15, blank=True)
    background_color = models.CharField(max_length=15, blank=True)

    def clean(self):
        if not self.header_title and not self.image:
            raise ValidationError({"header_title": "header title and image At least one of this should be"})

    class Meta:
        db_table = "header_site"
