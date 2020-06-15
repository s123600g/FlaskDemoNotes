FROM nginx:stable

ENV web_project="web_data"
ENV web_port=5001

RUN apt-get update && apt-get install -y curl python3 python3-dev python3-pip nano gcc default-libmysqlclient-dev iputils-ping
RUN mkdir /web \
    && mkdir /web/${web_project} \
    && mkdir /etc/nginx/sites-enabled

COPY "nginx.conf" "/web"
COPY "web.conf" "/etc/nginx/sites-enabled"
COPY "requirements.txt" "/web"
COPY "start_up.sh" "/var/local"

RUN chmod 777 /var/local/start_up.sh

RUN pip3 install -r /web/requirements.txt

RUN mv /etc/nginx/nginx.conf /etc/nginx/nginx_old.conf \
    && cp /web/nginx.conf /etc/nginx/

EXPOSE ${web_port}
CMD [ "/bin/bash", "-c" , "/var/local/start_up.sh ;"]