FROM python:2.7

WORKDIR /app
COPY techtrends/requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install -r requirements.txt

# Copy app code
COPY techtrends/ .

# Initialize DB
RUN python init_db.py

EXPOSE 3111
CMD ["python", "app.py"]