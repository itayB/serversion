FROM python:3-slim
ADD ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt
ADD ./serversion /serversion
CMD ["python", "-m", "serversion"]
