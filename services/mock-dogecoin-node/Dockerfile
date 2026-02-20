FROM python:3.12-slim

WORKDIR /app

RUN pip install flask requests

COPY . .

EXPOSE 22555

CMD ["python", "app.py"]
