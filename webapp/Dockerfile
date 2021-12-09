# fetches Python image based on Slim
FROM python:3.10-slim

# setup working directory
WORKDIR /src

# copy folder into working directory
COPY . /src

# install requirements
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "/src/run.py"]