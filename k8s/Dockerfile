FROM jupyterhub/k8s-hub:7f6781e
    
COPY --chown=1000:1000 page.html /usr/local/share/jupyterhub/templates/page.html
COPY --chown=1000:1000 page.less /usr/local/share/jupyterhub/static/less/page.less
COPY --chown=1000:1000 spawn_pending.html /usr/local/share/jupyterhub/templates/spawn_pending.html
COPY --chown=1000:1000 jupyter.png /usr/local/share/jupyterhub/static/images/jupyter.png
COPY --chown=1000:1000 favicon.ico /usr/local/share/jupyterhub/static/favicon.ico
COPY --chown=1000:1000 favicon.ico /usr/local/share/jupyterhub/static/images/favicon.ico


CMD ["jupyterhub", "--config", "/srv/jupyterhub_config.py"]
