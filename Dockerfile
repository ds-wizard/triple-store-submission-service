FROM python:3.8

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install .

EXPOSE 8080

ENV SUBMISSION_CONFIG /app/config.yml

CMD ["python", "-m", "aiohttp.web", "-H", "0.0.0.0", "-P", "8080", "triple_store_submitter:init_func"]
