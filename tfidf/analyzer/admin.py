from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    fields = (
        'document',
        'word_frequency'
    )
