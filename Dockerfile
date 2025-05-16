# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements to leverage layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run the bot as a module so that src/ is treated as a package
CMD ["python", "-m", "src.bot"]

