FROM python:3.9-slim
WORKDIR /app
COPY ~/.streamlit/config.toml /root/.streamlit/config.toml
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "main_page.py"]