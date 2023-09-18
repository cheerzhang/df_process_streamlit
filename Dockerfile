FROM python:3.9.6
WORKDIR /app
COPY requirements.txt ./requirements.txt
COPY . /app
RUN pip install -r requiremts.txt
EXPOSE 8501
ENTRYPOINT ["streamlit", "run"]
CMD ["main_page.py"]