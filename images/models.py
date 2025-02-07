from django.db import models
from hashlib import sha1
from base64 import b64encode
from django.utils.translation import gettext_lazy as _

from core.models import CreateMixin, UpdateMixin, SoftDeleteMixin
from images.validators import validate_image_size


class Image(CreateMixin, UpdateMixin, SoftDeleteMixin):
    title = models.CharField(max_length=128, null=True, blank=True)
    image = models.ImageField(width_field="width", height_field="height", upload_to="images/%Y/%m/%d",
                              validators=[validate_image_size],
                              help_text=_("max size is 5 MG"))

    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)

    file_hash = models.CharField(max_length=40, null=True, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True, help_text=_("file size as xx.b"))

    focal_point_x = models.PositiveIntegerField(null=True, blank=True)
    focal_point_y = models.PositiveIntegerField(null=True, blank=True)
    focal_point_width = models.PositiveIntegerField(null=True, blank=True)
    focal_point_height = models.PositiveIntegerField(null=True, blank=True)
    image_base64 = models.TextField(_("تبدیل به فورمت base64"), blank=True, null=True)

    @property
    def generate_hash(self):
        hasher = sha1()
        for c in self.image.chunks():
            hasher.update(c)
        return hasher.hexdigest()

    @property
    def encode_image(self):
        encode_b64 = b64encode(self.image.read())
        return encode_b64.decode("utf-8")

    def __str__(self):
        return f"{self.file_hash} && {self.title}"

    @property
    def image_url(self):
        return self.image.url if self.image else None

    def show_image_base64(self):
        d = 'data:image/png;base64,{}'.format(self.image_base64)
        return d

    def save(self, *args, **kwargs):
        self.image_base64 = self.encode_image
        self.file_hash = self.generate_hash
        self.file_size = self.image.size
        return super().save(*args, **kwargs)

    class Meta:
        db_table = "image"
        verbose_name = _("Image")
        verbose_name_plural = _("Images")
