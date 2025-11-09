# Use an official, lightweight Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app's code (application.py, static folder)
COPY . .

# Expose the port your app runs on
EXPOSE 5000

# The command to run your app using a production server (gunicorn)
# This uses the 'application' variable inside your 'application.py' file
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "application:application"]