# Use the official Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 8000
EXPOSE 8000

# Start the application
CMD ["gunicorn", "socialnetwork.wsgi:application", "--bind", "0.0.0.0:8000"]
