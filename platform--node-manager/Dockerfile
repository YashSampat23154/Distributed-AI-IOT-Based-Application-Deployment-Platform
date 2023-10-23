FROM python:3.10-alpine
WORKDIR /node_manager
COPY . /node_manager
RUN pip install -r /node_manager/requirements.txt
CMD ["python3", "/node_manager/main.py"]