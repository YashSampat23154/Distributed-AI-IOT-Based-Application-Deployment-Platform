FROM python:3.10-alpine
WORKDIR /deployer
COPY . /deployer
RUN pip install -r /deployer/requirements.txt
CMD ["python3", "/deployer/main.py"]
