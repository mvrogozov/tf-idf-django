import math
import re
from time import perf_counter

import pymorphy2
import chardet
from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, ListView

from .forms import DocumentForm
from .models import Document
from core.utils import count_tf, count_idfs


class DocumentCreateView(CreateView):
    template_name = 'analyzer/load_document.html'
    form_class = DocumentForm

    def form_valid(self, form):
        time_start = perf_counter()
        doc = form.save(commit=False)
        raw_data = form.cleaned_data['document'].read()
        try:
            data = raw_data.decode('utf-8')
        except UnicodeDecodeError:
            encoding = chardet.detect(raw_data)['encoding']
            data = raw_data.decode(encoding)
        freq = count_tf(
            data,
            settings.ANALYZER_MIN_WORD_LENGTH,
            normalize=True
        )
        doc.word_frequency = freq
        doc.time_processed = str(perf_counter() - time_start)
        doc.owner = self.request.user
        doc.save()
        return redirect('analyzer:report', doc.id)


class ReportView(ListView):
    template_name = 'analyzer/report.html'

    def get_queryset(self):
        self.doc = get_object_or_404(Document, pk=self.kwargs['document_id'])
        return self.doc

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        docs = Document.objects.all()
        docs_amount = docs.count()

        if self.doc.word_frequency:
            idfs = count_idfs(self.doc.word_frequency, docs)
            word_data = [
                (word, tf, idfs[word], tf * idfs[word])
                for word, tf in self.doc.word_frequency.items()
            ]

            word_data.sort(key=lambda x: x[2], reverse=True)

            paginator = Paginator(word_data, 50)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context['word_data_page'] = page_obj
        context.update({
            'filename': self.doc.document.name,
            'title': 'Анализ документа',
            'docs_amount': docs_amount,
        })
        return context
