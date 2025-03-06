# Usa a imagem oficial do Python 3.13.2 (versão slim)
FROM python:3.13.2-slim

# Instala o Node.js, npm, dbus e dependências gráficas
RUN apt-get update && \
    apt-get install -y curl gnupg dbus-x11 x11-apps xvfb \
    libgtk-3-0 \
    libnotify4 \
    libgdk-pixbuf2.0-0 \
    libxss1 \
    libasound2 \
    libnss3 \
    libx11-xcb1 \
    libxtst6 \
    libxrandr2 \
    libgconf-2-4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    x11-xserver-utils \
    libxcb-dri3-0 \
    libglib2.0-0 \
    libglu1-mesa \
    libgl1-mesa-glx \
    mesa-utils && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho no container
WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Instala as dependências do Python e do Node.js
RUN pip install --no-cache-dir -r requirements.txt && npm install

# Exponha a porta usada pelo Panel
EXPOSE 5006

# Executa o Panel em segundo plano e inicia o Electron com configurações seguras
CMD ["sh", "-c", "service dbus start && \
    panel serve monitor.py --port 5006 & \
    sleep 5 && \
    xvfb-run -a npx electron . --no-sandbox --disable-gpu --enable-logging"]

