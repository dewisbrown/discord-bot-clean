# Define language
FROM python:3.11

# Make app directory
RUN mkdir -p /app

# Define working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt requirements.txt 

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all other files in project directory
COPY . .

# Run the bot
CMD ["python", "bot.py"]
