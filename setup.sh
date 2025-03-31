#!/bin/bash

echo "Clonage du repo"
git clone https://github.com/TON_USER/LeagueGPT.git /root/LeagueGPT

cd /root/LeagueGPT

echo "Création du venv"
apt update
apt install -y python3-venv nginx certbot python3-certbot-nginx

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Redéploiement de Streamlit"
nohup streamlit run app/frontend/streamlit_app.py --server.port 8888 --server.address localhost &

echo "Setup terminé"
