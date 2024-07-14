sudo docker build -f dockerfile.client -t client-image .

sudo docker run -d --name client1 --network chord-network client-image
sudo docker run -d --name client2 --network chord-network client-image