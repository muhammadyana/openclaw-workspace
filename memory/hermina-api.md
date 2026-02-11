# Hermina Public API Documentation

## Base URL
**Production:** `https://api.herminahospitals.com/api/v1/`

## Key Endpoints

### 1. Articles
- **GET** `/public/articles` - Get all articles
  - Query params: `page`, `per_page`, `q` (search), `tagged_with`, `categoried_with`, `hospital_id`, `hospital_ids`
- **GET** `/public/articles/{id}` - Get article by ID/slug

### 2. Hospitals
- **GET** `/public/hospitals/` - Get all hospitals
  - Query params: `q`, `branch_id`, `latitude`, `longitude`
- **GET** `/public/hospitals/nearby` - Get nearby hospitals
  - Required: `lat`, `lng`
- **GET** `/public/hospitals/{id}` - Get hospital detail
- **GET** `/public/hospitals/{id}/videos` - Get hospital videos
- **GET** `/public/hospitals/{id}/sepecial-offers` - Get hospital special offers

### 3. Companies
- **GET** `/public/companies` - Get all companies
- **GET** `/public/companies/{slug}/` - Get company detail
- **GET** `/public/companies/{company_slug}/service_packages` - Get service packages
- **GET** `/public/companies/{company_slug}/service_packages/{package_slug}` - Get package detail

### 4. Short Videos
- **GET** `/public/short-videos` - Get short videos
- **GET** `/public/short-videos/{slug}` - Get video by slug
- **GET** `/public/short-videos/tags` - Get video tags

## Example Usage
```bash
# Get all hospitals
curl https://api.herminahospitals.com/api/v1/public/hospitals/

# Get nearby hospitals
curl "https://api.herminahospitals.com/api/v1/public/hospitals/nearby?lat=-6.8956884&lng=107.5888632"

# Get articles by hospital
curl "https://api.herminahospitals.com/api/v1/public/articles?hospital_id=7"
```

## Important Notes
- Use **Production URL**: `https://api.herminahospitals.com/api/v1/`
- All endpoints return JSON with `success`, `code`, `status`, `message`, `data` structure
- Pagination supported with `page` and `per_page` parameters
- Full OpenAPI spec saved in memory for reference
