FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for OpenCV (required by MTCNN/DeepFace)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install streamlit specific dependencies
RUN pip install --no-cache-dir streamlit streamlit-webrtc tf-keras fpdf2

# Copy all project files
COPY . .

# Expose Streamlit port
EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app/main.py"]
