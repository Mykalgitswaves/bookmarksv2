FROM --platform=linux/amd64 python:3.10-slim

# Create a non-root user 'appuser'
RUN adduser --disabled-password appuser

WORKDIR /home/appuser

# Update PATH so executables installed to .local/bin are found
ENV PATH="/home/appuser/.local/bin:${PATH}"

COPY requirements.txt /home/appuser
RUN pip install -r requirements.txt

COPY . /home/appuser

RUN mkdir -p src/utils/logging/logs

RUN chown -R appuser:appuser src/utils/logging/logs
RUN chmod -R 755 src/utils/logging/logs

EXPOSE 8000

USER appuser

ENV GUNICORN_WORKERS=1

CMD gunicorn -w $GUNICORN_WORKERS \
             -k uvicorn.workers.UvicornWorker \
             src.main:backend_app \
             --bind 0.0.0.0:8000
