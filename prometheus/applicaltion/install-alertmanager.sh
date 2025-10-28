docker run -d --name alertmanager -p 9093:9093 -v /data/apps/alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml bitnami/alertmanager
