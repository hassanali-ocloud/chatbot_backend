# Use slim Python base
FROM python:3.12

# set workdir
WORKDIR /app

# Install build deps then python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy app
COPY . .

# Create startup script
RUN echo '# Start FastAPI application\n\
uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers\n\
' > /app/start.sh && chmod +x /app/start.sh

# If you use Uvicorn, expose port 8000
ENV PORT=8000
EXPOSE 8000

# Run the startup script
CMD ["/app/start.sh"]
