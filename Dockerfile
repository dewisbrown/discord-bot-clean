# Define language
FROM python:3.11

# Make app directory
RUN mkdir -p /app

# Set newly created app directory as working directory
WORKDIR /app

# Copy .env file over
COPY .env .env

# Copy dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all other files to /app
COPY . .

# Run the bot
CMD ["python", "bot.py"]