FROM grafana/grafana

USER root
RUN apk update && apk add sqlite

USER grafana

COPY ./statistics/grafana.ini /etc/grafana/grafana.ini

#RUN grafana cli plugins install frser-sqlite-datasource
RUN grafana cli --pluginUrl https://github.com/fr-ser/grafana-sqlite-datasource/releases/download/v3.5.0/frser-sqlite-datasource-3.5.0.zip plugins install frser-sqlite-datasource

EXPOSE 8080
