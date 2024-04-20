# Use the official Python image with your desired version
FROM python:3.11

ARG DOPPLER_TOKEN
ENV DOPPLER_TOKEN=$DOPPLER_TOKEN

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ARG DB_ENGINE=${DB_ENGINE}
ENV DB_ENGINE=${DB_ENGINE}
ARG DB_HOST=${DB_HOST}
ENV DB_HOST=${DB_HOST}
ARG DB_NAME=${DB_NAME}
ENV DB_NAME=${DB_NAME}
ARG DB_PASSWORD=${DB_PASSWORD}
ENV DB_PASSWORD=${DB_PASSWORD}
ARG DB_PORT=${DB_PORT}
ENV DB_PORT=${DB_PORT}
ARG DB_USER=${DB_USER}
ENV DB_USER=${DB_USER}
ARG DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
ARG RANDOM_ORG_API_KEY=${RANDOM_ORG_API_KEY}
ENV RANDOM_ORG_API_KEY=${RANDOM_ORG_API_KEY}
ARG DEBUG=${DEBUG}
ENV DEBUG=${DEBUG}

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

ENTRYPOINT ["./start.sh"]

# Run migrations
#CMD ["poetry", "run", "python", "manage.py", "migrate"]
# Run server
#CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
