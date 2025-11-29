Generate SSL:

```bash
IP=$(ipconfig getifaddr en0) 
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=$IP"

echo "憑證產生完成，IP: $IP"
```