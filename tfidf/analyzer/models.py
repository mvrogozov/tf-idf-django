from django.db import models


class Document(models.Model):
    document = models.FileField(
        'документ',
    )
    word_frequency = models.JSONField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.document.name
