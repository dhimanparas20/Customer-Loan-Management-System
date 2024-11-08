# Pull official base image
FROM python:3.11-slim

# Set work directory
WORKDIR /app
COPY ./requirements.txt /app/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt    

# Copy project
COPY . /app/

# Expose port 80
EXPOSE 80

# Specify the command to run using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:80", "cas.wsgi:application"]