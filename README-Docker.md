# Docker container for the SMNAMonitoringApp

1. Create the `Dockerfile` file;
2. Create the `docker-compose.yml` file (optional);
3. Create the `requirements.txt` file (if necessary, manually edit the file):
    ```
    pip freeze > requirements.txt
    ```
4. Build the container:
    ```
    docker build -t smna-monitoring .
    ```
5. Run the container:
    ```
    docker run -p 5006:5006 smna-monitoring
    ```
6. If using the `docker-compose.yml` file, build and run the container:
    ```
    docker-compose up --build
    ```

---

carlos.bastarz@inpe.br (19/02/2025)
