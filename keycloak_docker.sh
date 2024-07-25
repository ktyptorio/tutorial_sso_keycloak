#!/bin/bash

# Function to handle errors
handle_error() {
  echo "Error: $1"
  exit 1
}

# Function to check if a package is installed
is_package_installed() {
  dpkg -l | grep -q $1
}

# Check if SSL certificate exists
if [ -e "server.crt.pem" ] && [ -e "server.key.pem" ]; then
  echo "SSL certificate already exists. Skipping generation."
else
  # SSL certificate profile template
  SSL_PROFILE_TEMPLATE="/tmp/ssl_profile_template.txt"

  cat <<EOL > "$SSL_PROFILE_TEMPLATE"
  [req]
  default_bits = 2048
  prompt = no
  default_md = sha256
  req_extensions = req_ext
  distinguished_name = dn

  [dn]
  C = ID
  ST = Jakarta
  L = Jakarta
  O = YourOrganization
  OU = YourUnit
  CN = yourdomain.com

  [req_ext]
  subjectAltName = @alt_names

  [alt_names]
  DNS.1 = yourdomain.com
  DNS.2 = *.yourdomain.com
EOL

  # Generate SSL certificate
  openssl req -newkey rsa:2048 -nodes \
    -keyout server.key.pem -x509 -days 3650 -out server.crt.pem \
    -config "$SSL_PROFILE_TEMPLATE" || handle_error "Failed to generate SSL certificate"

  chmod 755 server.key.pem || handle_error "Failed to set permissions for SSL certificate"
fi

# Run Keycloak in Docker
docker run \
  --name keycloak \
  -e KEYCLOAK_ADMIN=admin \
  -e KEYCLOAK_ADMIN_PASSWORD=password \
  -e KC_HTTPS_CERTIFICATE_FILE=/opt/keycloak/conf/server.crt.pem \
  -e KC_HTTPS_CERTIFICATE_KEY_FILE=/opt/keycloak/conf/server.key.pem \
  -v $PWD/server.crt.pem:/opt/keycloak/conf/server.crt.pem \
  -v $PWD/server.key.pem:/opt/keycloak/conf/server.key.pem \
  -p 8443:8443 -d \
  quay.io/keycloak/keycloak:25.0.2 \
  start-dev || handle_error "Failed to run Keycloak in Docker"

echo "Installation and setup completed successfully."
