# Use the official Python image with your desired version
FROM python:3.11

ARG DOPPLER_TOKEN
ENV DOPPLER_TOKEN=$DOPPLER_TOKEN

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install doppler
RUN apt-get install -y apt-transport-https ca-certificates curl gnupg && \
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" | tee /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && \
    apt-get -y install doppler

RUN mkdir /app

COPY pyproject.toml poetry.lock /app/

# Set the working directory in the container
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Copy the rest of the application code
COPY . /app/

# Run Django collectstatic. Use this line if you handle static files in your project.
# Make sure you have your Django settings properly configured for static files.
# RUN python manage.py collectstatic --noinput

EXPOSE 8000

RUN chmod +x ./start.sh

#ENTRYPOINT ["./start.sh"]

# Run migrations
CMD ["poetry", "run", "python", "manage.py", "migrate"]
# Run server
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
