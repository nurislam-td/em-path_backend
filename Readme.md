# Issue RSA private key + public key pair

## For access key

```shell
# Generate an RSA private key, of size 2048
openssl genrsa -out access-private.pem 2048
```

```shell
# Extract the public key from the key pair, which can be used in a certificate
openssl rsa -in access-private.pem -outform PEM -pubout -out access-public.pem
```

## For refresh key

```shell
# Generate an RSA private key, of size 2048
openssl genrsa -out refresh-private.pem 2048
```

```shell
# Extract the public key from the key pair, which can be used in a certificate
openssl rsa -in refresh-private.pem -outform PEM -pubout -out refresh-public.pem
```

**Get environment variable**

# Up database

**install docker**

```shell
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

```shell
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

**and run this command**

```shell
sudo docker compose up --build
# command should be running from docker-compose.yml directory
```

# Run FastAPI application

```shell
python app/main.py
```
