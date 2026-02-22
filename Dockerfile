FROM python:3.10.7

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy rest of application
COPY . .

EXPOSE 8004

# Run migrations before collectstatic to ensure database is ready
CMD bash -c "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8004 altered_datum_api.wsgi"