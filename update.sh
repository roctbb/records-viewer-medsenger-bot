git pull
sudo pip3 install -r requirements.txt
flask db migrate
flask db upgrade
sudo ./restart.sh
npm run build