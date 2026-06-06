FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN useradd -u 10000 nonrootuser
USER nonrootuser
EXPOSE 5000
HEALTHCHECK CMD curl --fail http://localhost:5000/health
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
