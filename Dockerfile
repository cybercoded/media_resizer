FROM python:3.8.5-alpine

# Upgrade pip and install system dependencies for Pillow
RUN apk add --no-cache \
    jpeg-dev zlib-dev freetype-dev libwebp-dev tiff-dev \
    gcc musl-dev python3-dev libffi-dev

# Copy requirements and install Python dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

# Copy application code to the container
COPY . /app

# Set the working directory
WORKDIR /app

# Copy entrypoint script and set it as executable
COPY ./entrypoint.sh /
RUN chmod +x /entrypoint.sh

# Define the entrypoint
ENTRYPOINT ["sh", "/entrypoint.sh"]