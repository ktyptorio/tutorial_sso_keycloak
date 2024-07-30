# Praktik Keycloak untuk Peningkatan Keamanan Autentikasi Aplikasi

Panduan ini akan memandu Anda melalui proses pengaturan dan penggunaan Keycloak untuk meningkatkan keamanan autentikasi aplikasi.

## Persiapan Teknis

1. Pastikan Anda memiliki Virtual Box atau VMWare yang terpasang.
2. Siapkan VM dengan Ubuntu Server 22.04 LTS.
3. Instal Docker:
   ```bash
   sudo nano docker-install.sh
   ```
   Salin dan tempelkan skrip berikut:
   ```bash
   #!/bin/bash
   for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done
   sudo apt-get update
   sudo apt-get install -y ca-certificates curl gnupg
   sudo install -m 0755 -d /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   sudo chmod a+r /etc/apt/keyrings/docker.gpg
   echo \
   "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
   "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   sudo apt-get update
   sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
   ```
   Jalankan skrip:
   ```bash
   sudo bash docker-install.sh
   ```

## Instalasi Keycloak

1. Clone repositori:
   ```bash
   sudo git clone https://github.com/ktyptorio/tutorial_sso_keycloak.git
   ```

2. Buat Docker network:
   ```bash
   sudo docker network create flask_network
   ```

3. Navigasi ke direktori yang telah di-clone dan jalankan Docker Compose:
   ```bash
   sudo bash keycloak_docker.sh
   ```

4. Akses Keycloak melalui browser Anda di `https://<IP>:8443/`

## Halaman Login Admin Keycloak

1. Masuk dengan kredensial berikut:
   - **Username**: admin
   - **Password**: password

## Membuat Realm Baru

1. Realm adalah batasan yang membatasi ruang lingkup manajemen identitas dan akses dalam Keycloak.
2. Klik `Create realm`.
3. Unduh file `realm_config.json` dari VM.
4. Klik `Browse` untuk mengunggah file tersebut sebagai resource file bagi realm yang sedang dibuat.
5. Klik `Create`.

## Membuat Client Secret untuk Aplikasi yang Akan Menggunakan SSO

1. Atur isian dengan kotak merah dengan IP aplikasi yang akan menggunakan SSO.
2. Pilih tab `Credentials`.
3. Pilih `Client Id and Secret`.
4. Regenerate dan copy `Client Secret`.

## Menjalankan Aplikasi Web

1. Build image aplikasi dengan menjalankan perintah berikut:
   ```bash
   sudo docker build -t flask-keycloak-app .
   ```

2. Jalankan container:
   ```bash
   sudo docker run --env-file .env -p 5000:5000 -d flask-keycloak-app
   ```

3. Cek container yang sudah dijalankan:
   ```bash
   sudo docker container ls
   ```

4. Jalankan aplikasi Web tersebut dengan mengakses:
   ```bash
   http://<IP>:5000/
   ```

## Registrasi Melalui Keycloak

1. Klik `Register` pada kotak dialog Login.
2. Masukkan isian sesuai dengan kolom yang diminta.
3. Buat password sesuai dengan kebijakan password yang sudah dibuat sebelumnya (Min 1 Special Character, Min 1 Upper case Character, Min 1 Lower case Character, Min panjang karakter 12).
4. Atur OTP dengan menggunakan Mobile Authenticator (Microsoft Auth, Google Auth, Free OTP).
5. Masukkan One Time Code dan nama perangkat.
6. Secara default, perlu melakukan proses verifikasi akun namun tahap ini dilewati. Lakukan verifikasi secara manual melalui halaman Administrator Keycloak.

## Dokumentasi Tambahan

Dokumentasi lebih lanjut dapat dipelajari pada:
[Keycloak Guides](https://www.keycloak.org/guides)

---

Panduan ini diharapkan dapat membantu Anda dalam mengatur dan menggunakan Keycloak untuk meningkatkan keamanan autentikasi aplikasi. Pastikan untuk mengganti `<IP>` dan `<container_id>` dengan nilai yang sesuai untuk setup Anda.