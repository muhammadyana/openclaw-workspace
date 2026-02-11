# Hermina API - Specialities (Spesialis) Documentation

## Get All Specialities
```
GET /public/specialities?page=1&per_page=20
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Speciality ID (e.g., "12", "9", "5") |
| `type` | string | "specialist" |
| `attributes.id` | integer | Numeric ID |
| `attributes.name_id` | string | Nama spesialis dalam Bahasa Indonesia |
| `attributes.name_en` | string | Nama spesialis dalam Bahasa Inggris |
| `attributes.name` | string | Nama default (biasanya sama dengan name_id) |
| `attributes.short_desc` | string | Deskripsi singkat |
| `attributes.description` | string | Deskripsi lengkap (HTML) |
| `attributes.description_id` | string | Deskripsi Bahasa Indonesia (HTML) |
| `attributes.description_en` | string | Deskripsi Bahasa Inggris (HTML) |
| `attributes.icon` | string | Nama file icon |
| `attributes.icon_url` | string | URL icon (S3 signed URL) |
| `attributes.slug` | string | URL slug (e.g., "klinik-gizi") |
| `attributes.is_highlight` | boolean | Apakah spesialis di-highlight |
| `attributes.doctors_count` | integer | Jumlah dokter dalam spesialis ini |
| `attributes.hospitals_count` | integer | Jumlah RS yang memiliki spesialis ini |
| `attributes.created_at` | string | Timestamp pembuatan |
| `attributes.updated_at` | string | Timestamp update |
| `attributes.head_banner.url` | string | URL banner utama |
| `attributes.head_banner.cover.url` | string | URL cover banner |

## Daftar Spesialis (dari API)

| ID | Nama Spesialis | Slug | Dokter | RS | Highlight |
|----|----------------|------|--------|-----|-----------|
| 12 | Klinik Gizi | klinik-gizi | 23 | 19 | ✅ |
| 9 | Kulit dan Kelamin (Dermatologi) | kulit-dan-kelamin-dermatologi-dan-venereologi | 139 | 49 | ✅ |
| 5 | Mata (Oftalmologi) | mata-optamologi | 157 | 45 | ✅ |
| 28 | Mikrobiologi Klinik | mikrobiologi-klinik | 1 | 1 | ❌ |
| 21 | Neurologi Anak Saraf | neurologi-anak-syaraf | 1 | 1 | ❌ |
| 29 | Okupasi | okupasi | 17 | 13 | ❌ |
| 31 | Onkologi Radiasi | onkologi-radiasi | 4 | 1 | ✅ |
| 35 | Orthopaedi & Traumatologi | bedah-ortopedi | 58 | 12 | ✅ |
| 7 | Paru-paru (Pulmonologi) | paru-paru-pulmonologi | 136 | 51 | ✅ |
| 27 | Patologi Anatomi | patologi-anatomi | 4 | 4 | ❌ |
| 26 | Patologi Klinik | patologi-klinik-clinical-pathology | 4 | 5 | ❌ |
| 13 | Pembiusan (Anestesi) | pembiusan-anestesi | 96 | 26 | ❌ |
| 4 | Penyakit Dalam | penyakit-dalam | 400 | 52 | ✅ |
| 11 | Psikologi | psikologi | 58 | 29 | ❌ |
| 22 | Radiologi | radiologi | 15 | 10 | ❌ |
| 16 | Rehabilitasi Medis | rehabilitasi-medis | 115 | 45 | ❌ |
| 6 | Saraf (Neurologi) | saraf-neurologi | 198 | 50 | ✅ |
| 34 | Spesialis Kedokteran Olahraga | spesialis-olahraga | 4 | 1 | ✅ |
| 36 | Spesialis Penerbangan | spesialis-penerbangan | 1 | 1 | ❌ |
| 39 | Spesialis Radiologi | spesialis-radiologi | 0 | 0 | ✅ |
| 15 | THT (Otolaringologi) | telinga-hidung-dan-tenggorokan-otolaringologi | 189 | 50 | ❌ |
| 18 | Terapi Okupasi | terapi-okupasi | 1 | 1 | ❌ |
| 25 | Urologi | urologi | 61 | 37 | ❌ |

## Sub-Spesialis (Contoh)

### Penyakit Dalam (Internal Medicine):
- Hepatologi
- Pulmonologi
- Ginjal-Hipertensi
- Alergi dan Imunologi
- Gastroenterologi-Hepatologi
- Geriatri
- Hematologi-Onkologi
- Kardiovaskular
- Endokrin
- Psikosomatik
- Reumatologi
- Penyakit Tropik-Infeksi
- Diabetes

### Saraf (Neurologi):
- Neurofisiologi
- Saraf Tepi
- Neurooftalmologi dan Neurootologi
- Neurotrauma
- Obat Tidur
- Nyeri dan Nyeri Kepala
- Neurobehavior dan Fungsi Luhur
- Neurogeriatrik
- Penyakit Serebrovaskular
- Neuroinfeksi
- Neuroonkologi
- Neurorestorasi
- Neuroediatri
- Neurointervensi

### Kulit dan Kelamin:
- Herpes
- Bedah Kulit
- Infeksi Menular Seksual (IMS)
- Dermatosis

## Get Speciality Detail
```
GET /public/specialities/{id}
```
Parameter `id` bisa berupa ID numerik atau slug.

## Get Speciality Special Services
```
GET /public/specialities/{id}/special-services
```
Mengambil layanan khusus yang tersedia untuk spesialis tertentu (misal: Cathlab, Bayi Tabung, Bank Darah Tali Pusat).

## Query Parameters
| Parameter | Fungsi |
|-----------|--------|
| `page` | Halaman |
| `per_page` | Jumlah per halaman |

## Related Endpoints
- `/public/doctors?speciality_id={id}` - Cari dokter by spesialis
- `/public/hospitals?speciality_id={id}` - Cari RS by spesialis

## Catatan
- Total 39+ spesialis tersedia di Hermina
- Spesialis dengan `is_highlight=true` ditampilkan secara prominent
- Icon URL adalah S3 signed URL dengan expiry 1 jam
- Deskripsi tersedia dalam 3 bahasa: ID, EN, dan default
