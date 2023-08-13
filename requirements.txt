# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run main.py when the container launches
CMD ["python", "main.py"]
