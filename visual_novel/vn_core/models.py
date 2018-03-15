import os
from PIL import Image

from django.conf import settings
from django.db import models

from core.models import PublishModel
from cinfo.models import Longevity, Genre, Tag, Studio, Staff, StaffRole


def posters_directory_path(instance, filename):
    return os.path.join(settings.MEDIA_VN_POSTER_DIRECTORY, filename)


def screenshots_directory_path(instance, filename):
    return os.path.join(settings.MEDIA_VN_SCREENSHOTS_DIRECTORY, filename)


def screenshots_mini_directory_path(instance, filename):
    return os.path.join(settings.MEDIA_VN_SCREENSHOTS_MINI_DIRECTORY, filename)


class VisualNovel(PublishModel):
    title = models.CharField(verbose_name='название', max_length=256)
    alternative_title = models.CharField(verbose_name='альтернативные названия', max_length=500, default='')
    description = models.TextField(verbose_name='описание', max_length=8000, default='')
    photo = models.ImageField(verbose_name='фотография', upload_to=posters_directory_path,
                              null=False, blank=False)
    date_of_release = models.DateField(verbose_name='дата релиза')
    vndb_id = models.IntegerField(verbose_name='id на VNDb')
    steam_link = models.CharField(verbose_name='ссылка в Steam', max_length=400, null=True, blank=True)
    longevity = models.ForeignKey(Longevity, verbose_name='продолжительность', on_delete=models.PROTECT,
                                  null=True, blank=True)
    genres = models.ManyToManyField(Genre, through='VNGenre', verbose_name='жанры', blank=True)
    tags = models.ManyToManyField(Tag, through='VNTag', verbose_name='тэги', blank=True)
    studios = models.ManyToManyField(Studio, through='VNStudio', verbose_name='студии', blank=True)
    staff = models.ManyToManyField(Staff, through='VNStaff', verbose_name='создатели', blank=True)
    alias = models.TextField(verbose_name='алиас (до 30 символов)', max_length=30, default='')

    class Meta:
        db_table = 'vncore'
        verbose_name = 'Визуальная новелла'
        verbose_name_plural = 'Визуальные новеллы'

    def __str__(self):
        return self.title


class VNGenre(models.Model):
    visual_novel = models.ForeignKey(VisualNovel, on_delete=models.PROTECT)
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT, related_name='genres_set')
    weight = models.IntegerField(verbose_name='вес', default=0)

    class Meta:
        db_table = 'vns_to_genres'
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.genre.title


class VNTag(models.Model):
    visual_novel = models.ForeignKey(VisualNovel, on_delete=models.PROTECT)
    tag = models.ForeignKey(Tag, on_delete=models.PROTECT, related_name='tags_set')
    weight = models.IntegerField(verbose_name='вес', default=0)

    class Meta:
        db_table = 'vns_to_tags'
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.tag.title


class VNStudio(models.Model):
    visual_novel = models.ForeignKey(VisualNovel, on_delete=models.PROTECT)
    studio = models.ForeignKey(Studio, on_delete=models.PROTECT, related_name='studios_set')
    weight = models.IntegerField(verbose_name='вес', default=0)

    class Meta:
        db_table = 'vns_to_studios'
        verbose_name = 'Студия'
        verbose_name_plural = 'Студии'

    def __str__(self):
        return self.studio.title


class VNStaff(models.Model):
    visual_novel = models.ForeignKey(VisualNovel, on_delete=models.PROTECT)
    staff = models.ForeignKey(Staff, on_delete=models.PROTECT, related_name='staff_set')
    role = models.ForeignKey(StaffRole, on_delete=models.PROTECT)
    weight = models.IntegerField(verbose_name='вес', default=0)

    class Meta:
        db_table = 'vns_to_staff'
        verbose_name = 'Создатель'
        verbose_name_plural = 'Создатели'

    def __str__(self):
        return self.staff.title


class VNScreenshot(PublishModel):
    title = models.CharField(verbose_name='подпись', max_length=256, null=True, blank=True)
    image = models.ImageField(verbose_name='фотография', upload_to=screenshots_directory_path,
        null=True, blank=True)
    miniature = models.ImageField(verbose_name='миниатюра', upload_to=screenshots_mini_directory_path,
        null=True, blank=True, editable=False)

    class Meta:
        db_table = 'vn_screenshot'
        verbose_name = 'Скриншот'
        verbose_name_plural = 'Скриншоты'

    def old_miniature_path_if_changed(self):
        try:
            old_miniature = VNScreenshot.objects.get(pk=self.pk).image
            if self.image != old_miniature:
                return old_miniature.path
        except VNScreenshot.DoesNotExist:
            pass
        except ValueError:
            pass
        return None

    def update_miniature(self, mini_width=150):
        if not self.image:
            return
        filename = os.path.basename(self.image.name)
        path = os.path.join(settings.MEDIA_VN_SCREENSHOTS_MINI_DIRECTORY, filename)
        new_path = os.path.join(settings.MEDIA_ROOT, path)
        if os.path.isfile(new_path):
            return
        image = Image.open(self.image.path)
        th_image = image.copy()
        size = (mini_width, int(float(mini_width) * float(self.image.height) / float(self.image.width)))
        th_image.thumbnail(size, Image.ANTIALIAS)
        th_image.save(new_path)
        self.miniature = path
        return path

    def delete_images(self):
        try:
            obj = VNScreenshot.objects.get(pk=self.pk)
        except VNScreenshot.DoesNotExist:
            return
        # Delete miniature from file system
        try:
            path_mini = obj.miniature.path
            if os.path.isfile(path_mini):
                os.remove(path_mini)
        except ValueError:
            pass
        # Delete main image from file system
        try:
            path = obj.image.path
            if os.path.isfile(path):
                os.remove(path)
        except ValueError:
            pass

    def save(self, *args, **kwargs):
        old_miniature = self.old_miniature_path_if_changed()
        if old_miniature:
            self.delete_images()
        super(VNScreenshot, self).save(*args, **kwargs)
        self.update_miniature()
        super(VNScreenshot, self).save(*args, **kwargs)

    def delete(self, force=True):
        if force:
            self.delete_images()
            super(VNScreenshot, self).delete()
        else:
            self.is_published = False
            super(VNScreenshot, self).save()
