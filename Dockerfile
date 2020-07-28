FROM hulkinbrain/docker-opencv2
USER root
WORKDIR /usr/src/app

COPY requirements_aws.txt ./
RUN pip install --no-cache-dir -r requirements_aws.txt

COPY . .

RUN [ "echo", "'hiMaxxxim06'" ]
RUN [ "pwd" ]
RUN [ "ls" ]
CMD [ "python", "./start_in_aws.py" ]
