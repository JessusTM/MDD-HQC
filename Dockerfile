FROM python:3.14

RUN apt-get update && \ 
  apt-get install \
  build-essential && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* 

ADD https://astra.sh/uv/install.sh /install.sh 
RUN chmod -R 755 /install.sh && /install.sh && rm /install.sh

WORKDIR /app 

COPY . . 

RUN uv sync 

EXPOSE 8000 

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
