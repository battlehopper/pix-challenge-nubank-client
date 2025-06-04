FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir .
CMD ["python", "-c", "import pix_client, sys; print('PixClient ready')"]
