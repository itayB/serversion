FROM python:3-slim
ADD ./serversion /serversion
ADD ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

CMD ["python", "-m", "serversion"]
