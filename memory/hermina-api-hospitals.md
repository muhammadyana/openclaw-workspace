# Hermina API - Hospitals List Documentation

## Get All Hospitals
```
GET /public/hospitals?page=1&per_page=20
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Hospital ID (e.g., "7", "13", "3") |
| `type` | string | "hospitals" |
| `attributes.name` | string | Hospital name (e.g., "Hermina Pasteur") |
| `attributes.address` | string | Full address |
| `attributes.latitude` | string | Latitude for maps |
| `attributes.longitude` | string | Longitude for maps |
| `attributes.branch` | string | Branch name (e.g., "Pasteur") |
| `attributes.provincy_name` | string | Province (e.g., "JAWA BARAT") |
| `attributes.doctors_count` | integer | Number of doctors |
| `attributes.slug` | string | URL slug (e.g., "hermina-pasteur") |
| `attributes.contact_phone` | string | Phone number |
| `attributes.call_center` | string | Call center number |
| `attributes.wa_number` | string | WhatsApp number |
| `attributes.appointment_method` | string | "afya" or other |
| `attributes.available_for_appointment` | boolean | Can book appointment |

## Sample Hospitals (from API)

### Bandung Area
- **Hermina Pasteur** (ID: 7) - 188 doctors
- **Hermina Arcamanik** (ID: 13) - 156 doctors
- **Hermina Soreang** (ID: 47) - 78 doctors

### Jakarta Area
- **Hermina Kemayoran** (ID: 2) - 221 doctors
- **Hermina Podomoro** (ID: 27) - 169 doctors
- **Hermina Jatinegara** (ID: 1) - 246 doctors
- **Hermina PIK Dua** (ID: 58) - 50 doctors

### Bekasi Area
- **Hermina Bekasi** (ID: 3) - dr. Brilianingsih
- **Hermina Galaxy** (ID: 14) - 155 doctors
- **Hermina Grand Wisata** (ID: 12) - dr. Brilianingsih Agustin
- **Hermina Metland Cibitung** (ID: 46) - 87 doctors

### Other Major Cities
- **Hermina Medan** (ID: 26) - 125 doctors
- **Hermina Makassar** (ID: 24) - 133 doctors
- **Hermina Samarinda** (ID: 28) - 125 doctors
- **Hermina Padang** (ID: 31) - 113 doctors
- **Hermina Palembang** (ID: 15) - 197 doctors
- **Hermina Yogyakarta** (ID: 22) - 111 doctors
- **Hermina Surabaya/UBAYA** (ID: 52) - 120 doctors

## Query Parameters
- `page` - Page number
- `per_page` - Items per page
- `q` - Search query
- `branch_id` - Filter by branch
- `latitude` + `longitude` - For nearby search

## Related Endpoint
- `/public/hospitals/nearby?lat=xx&lng=yy` - Get nearby hospitals
