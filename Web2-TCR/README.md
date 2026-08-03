# Web Challenge #2 - Who Are You?

## Deskripsi

Sebuah website punya halaman login. Kamu berhasil masuk sebagai `user` biasa...
tapi flagnya cuma muncul kalau kamu `admin`. Gimana caranya?

## File

- `index.html` — tampilan frontend
- `app.py` — backend Flask (dijalankan via Docker)
- `docker-compose.yml` — konfigurasi Docker

Akses di: linkny

## Credentials

| Username | Password |
| -------- | -------- |
| player   | ctf2026  |
| user     | password |

## Flag

Format flag: `tecart{...}`

## Hint

- Setelah login, coba buka **DevTools** → tab **Application** → **Cookies**
- Perhatiin nilai cookie `role` yang tersimpan
- Cookie itu di-encode pakai **Base64**
- Coba decode, liat isinya... terus pikirin, bisa gak diubah?

## Author

L3L3
