from django.db import models


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

    def __str__(self):
        return self.document.name
