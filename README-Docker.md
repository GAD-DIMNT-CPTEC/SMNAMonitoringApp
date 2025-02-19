# Imagem Docker para o SMNAMonitoringApp

## Criação da imagem

1. Criar o arquivo `Dockerfile`;
2. Criar o arquivo `docker-compose.yml` (opcional);
3. Criar o arquivo `requirements.txt` (editar manualmente, se necessário):
    ```
    pip freeze > requirements.txt
    ```
4. Construir o container:
    ```
    docker build -t smna-monitoring .
    ```
5. Executar o container:
    ```
    docker run -p 5006:5006 smna-monitoring
    ```
6. Construir e executar o container com o `docker-compose.yml`:
    ```
    docker-compose up --build
    ```

---

carlos.bastarz@inpe.br (19/02/2025)
