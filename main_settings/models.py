from django.db import models
from django.contrib.gis.db.models import PointField
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from django.core.validators import FileExtensionValidator

from accounts.validators import MobileRegexValidator
from core.models import SoftDeleteMixin, UpdateMixin, CreateMixin


class HeaderSite(CreateMixin, UpdateMixin, SoftDeleteMixin):
    header_title = models.CharField(_("نام هدر"), max_length=20)
    link = models.URLField(_("ادرس"))

    def __str__(self):
        return self.header_title

    class Meta:
        db_table = 'header_site'
        verbose_name = _("هدر سایت")
        verbose_name_plural = _("هدر سایت")


class SiteSettings(CreateMixin, UpdateMixin, SoftDeleteMixin):
    site_logo = models.ImageField(_("عکس لوگوی سایت"), upload_to='main_settings/site_logo')
    header_image = models.ImageField(_("عکس هدر سایت"), upload_to='main_settings/header_image')
    header_video = models.FileField(_("فیلم معرفی"), validators=[FileExtensionValidator(allowed_extensions=("mp4",))])
    header_video_explain = models.TextField(_("توضیح در مورد معرفی ویدیو"))
    title_main = models.CharField(_("عنوان بدنه"))
    title_main_explain = models.TextField(_("توضیح عنوان بدنه"))
    footer_address = models.TextField(_("ادرس ها"))
    about_us_explain = models.TextField(_("درباره ما"))
    copy_right_text = models.CharField(_("متن کپی و رایت"), max_length=255)
    is_main_settings = models.BooleanField(_("تنظیم اصلی سایت باشد"))
    phone = ArrayField(verbose_name=_("شماره تماس با ما"), size=5, base_field=models.CharField(max_length=11),
                       help_text=_("برای وارد کردن چندین شماره تماس با کاما از هم دیگر جدا کنید"),
                       validators=[MobileRegexValidator()])
    location = PointField()


class TopStudent(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student_name = models.CharField(_("نام دانش اموز"), max_length=50)
    student_image = models.ImageField(_("عکس دانش اموز"), upload_to='main_settings/top_student')
    explain = models.CharField(_("توضیح در مورد دانش اموز"), max_length=255)
    is_publish = models.BooleanField(_('انتشار در سایت'), default=True)

    def __str__(self):
        return self.student_name

    class Meta:
        db_table = 'top_student'
        verbose_name = _("برترین دانش اموزان")
        verbose_name_plural = _("برترین دانش اموزان")


class FrequencyAskQuestion(CreateMixin, UpdateMixin, SoftDeleteMixin):
    question = models.CharField(_("عنوان سوال"), max_length=255)
    explain_question = models.TextField(_("توضیح در مورد سوال"))

    def __str__(self):
        return self.question

    class Meta:
        db_table = 'frequency_ask_question'
        verbose_name = _("سوالات متداول")
        verbose_name_plural = _("سوالات متداول")


class FooterLogo(CreateMixin, UpdateMixin, SoftDeleteMixin):
    logo = models.ImageField(_("عکس های فوتر"), upload_to='main_settings/footer_logo')
    logo_url = models.URLField(_("ادرس لوگو"))
    is_publish = models.BooleanField(_("انشتار در سایت"), default=True)

    def __str__(self):
        return self.logo_url

    class Meta:
        db_table = 'footer_logo'
        verbose_name = _("عکس فوتر")
        verbose_name_plural = _("عکس های فوتر")


class FooterSocial(CreateMixin, UpdateMixin, SoftDeleteMixin):
    social_image = models.ImageField(_("عکس شبکه اجتماعی"), upload_to='main_settings/footer_social')
    social_url = models.URLField(_("ادرس شبکه اجتماعی"))
    is_publish = models.BooleanField(_("قابلیت انتشار"), default=True)

    def __str__(self):
        return self.social_url

    class Meta:
        db_table = 'footer_social'
        verbose_name = _("شبکه اجتماعی")
        verbose_name_plural = _("شبکه های اجتماعی")


class SliderImage(CreateMixin, UpdateMixin, SoftDeleteMixin):
    image = models.ManyToManyField("images.Image", related_name='main_slider_image')
    slider_image_explain = models.CharField(_("توضیح"), max_length=255)
    slider_url = models.URLField(_("ادرس اسلایدر"))
    is_publish = models.BooleanField(_("انتشار"), default=True)

    def __str__(self):
        return self.slider_url

    class Meta:
        db_table = 'slider_image'
        verbose_name = _("عکس اسلایدر")
        verbose_name_plural = _("عکس اسلادر ها")
