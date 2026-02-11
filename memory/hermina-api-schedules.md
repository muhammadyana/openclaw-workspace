# Hermina API - Doctor Schedules Endpoint Documentation

## Doctor Schedule Endpoints

### 1. Get Doctor Detail (Base Info)
```
GET /public/doctors/{slug}
```

**Response Fields for Schedules:**
- `hospitals[].id` - Hospital ID (for schedule queries)
- `hospitals[].setting.appointment_method` - e.g., "afya"
- `hospitals[].setting.available_for_appointment` - boolean

### 2. Get Schedule (Table Format)
```
GET /public/doctors/{slug}/schedules?schedule_type={type}&type=table
```

**Schedule Types:**
- `specialist` - Jadwal reguler
- `executive` - Jadwal eksekutif

**Response Structure:**
```json
{
  "data": {
    "Hospital Name": [
      {
        "id": "24",
        "day": "wednesday",
        "day_integer": "3",
        "from_time": "09:00",
        "to_time": "12:00",
        "time": "09:00-12:00",
        "schedule_type": "executive",
        "unit_id": "24",
        "clinic_name": "Klinik Akupunktur Medik Padma",
        "appointment_method": "afya"
      }
    ]
  }
}
```

### 3. Get Schedule (Calendar Format)
```
GET /public/doctors/{slug}/schedules?hospital_id={id}&type=calendar&appointment_method={method}&schedule_type={type}&from_date={DD-MM-YYYY}&to_date={DD-MM-YYYY}
```

**Parameters:**
- `hospital_id` - From doctor detail response
- `type=calendar` - Return calendar format
- `appointment_method` - e.g., "afya"
- `schedule_type` - e.g., "executive"
- `from_date` - Format: DD-MM-YYYY
- `to_date` - Format: DD-MM-YYYY

**Response Structure:**
```json
{
  "data": [
    {
      "id": "24",
      "schedule_id": "24",
      "time": "09:00-12:00",
      "from_time": "09:00",
      "to_time": "12:00",
      "date": "2026-02-11",
      "day": "wednesday",
      "doctor_name": "dr. Brilianingsih Agustin Aribowo, Sp.Ak",
      "afya_doctor_id": "2974",
      "schedule_type": "executive",
      "day_integer": 3,
      "slots": 30,
      "clinic_name": "Klinik Akupunktur Medik Padma",
      "schedule_status": "Regular Schedule"
    }
  ]
}
```

## Example: dr. Brilianingsih A. A, SpAk

### Jadwal Praktek (Executive):

| Hari | Tanggal | Jam | Klinik | Slots |
|------|---------|-----|--------|-------|
| Rabu | 11 Feb 2026 | 09:00-12:00 | Klinik Akupunktur Medik Padma | 30 |
| Rabu | 18 Feb 2026 | 09:00-12:00 | Klinik Akupunktur Medik Padma | 30 |
| Rabu | 25 Feb 2026 | 09:00-12:00 | Klinik Akupunktur Medik Padma | 30 |
| Jumat | (tiap minggu) | 16:00-18:00 | Klinik Akupunktur Medik Padma | - |
| Sabtu | (tiap minggu) | 09:00-12:00 | Klinik Akupunktur Medik Padma | - |

### Jadwal Regular (Table):
- **Rabu**: 09:00-12:00
- **Jumat**: 16:00-18:00
- **Sabtu**: 09:00-12:00

### Lokasi:
- **Hermina Bekasi**
- **Klinik**: Klinik Akupunktur Medik Padma
- **Appointment Method**: afya

## Day Integer Mapping:
- 0 = Sunday (Minggu)
- 1 = Monday (Senin)
- 2 = Tuesday (Selasa)
- 3 = Wednesday (Rabu)
- 4 = Thursday (Kamis)
- 5 = Friday (Jumat)
- 6 = Saturday (Sabtu)

## Workflow untuk Cek Jadwal Dokter:
1. Cari dokter: `GET /public/doctors?q={nama}`
2. Ambil detail: `GET /public/doctors/{slug}` → dapat hospital_id
3. Cek jadwal table: `GET /public/doctors/{slug}/schedules?schedule_type=executive&type=table`
4. Cek jadwal calendar: `GET /public/doctors/{slug}/schedules?hospital_id={id}&type=calendar&from_date=DD-MM-YYYY&to_date=DD-MM-YYYY`
