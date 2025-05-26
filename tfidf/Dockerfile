FROM python:3.10-slim
RUN apt-get update
WORKDIR /app
COPY requirements/requirements.txt /app
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt --no-cache-dir

COPY tfidf/ ./tfidf
COPY analyzer/ ./analyzer
COPY api/ ./api
COPY templates/ ./templates
COPY static/ ./static
COPY manage.py .
LABEL author='mv_rogozov'
CMD ["gunicorn", "tfidf.wsgi:application", "--bind", "0:8000", "--reload", "--timeout", "400"]
