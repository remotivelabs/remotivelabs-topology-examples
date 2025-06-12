FROM python:3.13-slim

RUN pip install \
    jupyterlab==4.3.4 \
    ipywidgets==8.1.5 \
    remotivelabs-broker==0.9.0b3 \
    remotivelabs-topology==0.9.1

RUN jupyter labextension enable --py widgetsnbextension

CMD ["jupyter", "lab", "--allow-root"]
