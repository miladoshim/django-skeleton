FROM python:3.13

RUN mkdir /app

WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

RUN pip install --upgrade pip 

COPY ./requirements /requirements

# COPY ./scripts /scripts

COPY ./src /src

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN chmod -R +x /scripts && \
mkdir -p /vol/web/static && \
mkdir -p /vol/web/media && \
adduser --disabled-password --no-create-home djshop && \
chown -R djshop:djshop /vol && \
chmod -R 755 /vol

ENV PATH="/scripts:/py/bin:$PATH"

USER djshop

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]