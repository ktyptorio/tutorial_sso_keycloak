# Gunakan image dasar Python
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh project
COPY . /app

# Set environment variables untuk Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose port 5000
EXPOSE 5000

# Jalankan aplikasi Flask
CMD ["flask", "run"]
