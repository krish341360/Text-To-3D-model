FROM openfabric/tee-python-cpu:dev

# Install system dependencies
RUN apt-get update && apt-get install -y curl

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy only necessary files for Poetry installation
COPY pyproject.toml ./

# Install dependencies using Poetry
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --upgrade poetry && \
    python3 -m poetry install --only main && \
    rm -rf ~/.cache/pypoetry/{cache,artifacts}
    # python3 -m pip install openfabric-pysdk
# Copy the rest of the source code into the container
RUN pip install ollama

RUN pip install gradio

# Add new file
COPY gradio_app.py .

COPY . .

# Expose ports (Ollama + Flask)
EXPOSE 11434 8888

# Start Ollama service and preload Mistral model
CMD ["sh", "start.sh"]
