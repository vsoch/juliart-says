FROM continuumio/miniconda3

# docker build -t vanessa/juliart-says .

WORKDIR /code
COPY . /code
RUN pip install imageio &&  \
    pip install juliart>=0.0.14
ENTRYPOINT ["python", "/code/juliasays.py"]
