FROM python:3.11-slim
WORKDIR /app

# Set environment variables for Poetry and Python
ENV PYTHONPATH=/app/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/opt/poetry/cache \
    POETRY_HOME=/opt/poetry

ENV PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    libxml2-dev \
    libxslt-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && chmod +x /opt/poetry/bin/poetry

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Configure Poetry and install dependencies (without installing the project itself)
RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true \
    && poetry install --only=main --no-root \
    && rm -rf $POETRY_CACHE_DIR

# Copy project files
COPY src/ ./src/

# Create README.md if it doesn't exist
RUN touch README.md

# Create data directory for output
RUN mkdir -p /app/data

# Make sure the virtual environment is activated
ENV PATH="/app/.venv/bin:$PATH"

# Default command - run the API
CMD ["uvicorn", "module_1.api.main:app", "--host", "0.0.0.0", "--port", "8000"]