FROM python:3.10-slim
WORKDIR /app
RUN pip install --no-cache-dir pdfplumber
COPY extract_fontsize_headings.py .
CMD ["python", "extract_fontsize_headings.py"]
