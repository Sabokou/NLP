# fetches Python image based on Slim
FROM python:3.10-slim

# setup working directory
WORKDIR /src

# copy folder into working directory
COPY ./webapp /src
COPY ./QuestionGenerator/qg.py /src

# install requirements
COPY /webapp/requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "/src/run.py"]