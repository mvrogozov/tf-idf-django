from django.shortcuts import render, redirect
from django.views.generic import CreateView

from .forms import DocumentForm


class DocumentCreateView(CreateView):
    template_name = 'analyzer/load_document.html'
    form_class = DocumentForm

    def form_valid(self, form):
        post = form.save(commit=False)
        #post.author = self.request.user
        post.save()
        return redirect('analyzer:index')

    # def get_context_data(self, **kwargs):
    #     context = super(PostCreateView, self).get_context_data(**kwargs)
    #     context.update({
    #         'is_edit': False,
    #     }
    #     )
    #     return context
