FROM hulkinbrain/docker-opencv2
USER root
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN [ "echo", "'hiMaxxxim07'" ]
RUN [ "pwd" ]
RUN [ "ls" ]
CMD [ "python", "./start_in_aws.py" ]
