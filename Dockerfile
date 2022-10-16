FROM python:3.10.7
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
CMD ["/bin/bash"]

# CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

#FROM continuumio/miniconda3
#WORKDIR /app
#COPY environment.yml .
#RUN conda env create -f environment.yml
#SHELL ["conda", "run", "-n", "myenv", "/bin/bash", "-c"]
#RUN echo "Hello World"
#ENTRYPOINT ["/bin/bash"]

# Demonstrate the environment is activated:
#RUN echo "Make sure flask is installed:"
#RUN python -c "import flask"

# The code to run when container is started:
#COPY run.py .
#ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "myenv", "python", "run.py"]

# FROM continuumio/anaconda3:2020.11

#COPY . .
#RUN conda env create
#RUN conda run -n nyc-taxi-fare-prediction-deployment-example \
#  python -m pip install --no-deps -e .
#CMD [ \
#  "conda", "run", "-n", "nyc-taxi-fare-prediction-deployment-example", \
#  "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "nyc_taxi_fare.serve:app" \
#]

