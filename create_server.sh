sudo docker build -f dockerfile.server -t server-image .

sudo docker run -d --name server1 --network chord-network server-image
sudo docker run -d --name server2 --network chord-network server-image