from django.contrib import admin

from .models import Collection, Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    fields = (
        'document',
        'word_frequency',
        'time_processed',
        'owner'
    )
    list_filter = ('owner', 'document')
    search_fields = ('owner__username', 'document')


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    fields = (
        'owner',
        'documents'
    )
    filter_horizontal = ('documents',)
    list_filter = ('owner', 'documents')
    search_fields = ('owner__username',)
