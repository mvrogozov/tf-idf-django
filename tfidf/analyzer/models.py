from django.db import models
from django.conf import settings


User = settings.AUTH_USER_MODEL


class Document(models.Model):
    document = models.FileField(
        'документ',
    )
    word_frequency = models.JSONField(
        null=True,
        blank=True,
        verbose_name='частоты слов'
    )
    time_processed = models.FloatField(
        null=True,
        blank=True,
        verbose_name='время обработки, c'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь',
        related_name='document',
        blank=True,
        null=True
    )

    def delete(self, *args, **kwargs):
        if self.document:
            self.document.storage.delete(self.document.name)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f'{self.id} {self.document.name}'


class Collection(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь',
        related_name='collection',
        blank=True,
        null=True
    )
    documents = models.ManyToManyField(
        to=Document,
        blank=True,
        related_name='collection',
        verbose_name='документы'
    )

    def __str__(self):
        return (
            f'{self.owner.username} {self.id}' if self.owner else str(self.id)
        )
