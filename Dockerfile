FROM python:3.11

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock /app/

#RUN poetry install
#RUN poetry install --no-root
RUN poetry install --no-root && poetry show --tree

#COPY app /app
ADD app /app

CMD ["poetry", "run", "python", "main.py"]

