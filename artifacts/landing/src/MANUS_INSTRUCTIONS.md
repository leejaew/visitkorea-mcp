# Manus AI — Instructions for VisitKorea MCP

## What This MCP Is

This MCP server provides direct, structured access to the **Korea Tourism Organization (KTO) General Tourism dataset**, officially published on [data.go.kr](https://www.data.go.kr/data/15101753/openapi.do) under the service ID `EngService2`. The data covers all major tourism categories across South Korea — tourist attractions, cultural facilities, accommodations, restaurants, shopping venues, leisure and sports facilities, and festivals and events.

The server exposes **14 tools** over Streamable HTTP. Each tool wraps one API endpoint from the KTO open API, normalises the response, and returns clean structured data. No data is cached or synthesised — every call returns live data from the official KTO dataset.

---

## When to Use This MCP

Activate tools from this MCP whenever the user's request involves any of the following:

- Finding **tourist attractions, cultural sites, palaces, museums, or natural landscapes** in South Korea
- Recommending or comparing **hotels, guesthouses, pensions, or other accommodation** in a Korean city or region
- Finding **restaurants, local food, or dining options** anywhere in South Korea
- Discovering **Korean festivals, performances, or cultural events** within a date range
- Recommending **shopping districts, markets, or duty-free zones** in Korea
- Finding **leisure sports, outdoor activities, or recreational facilities** in a region
- Retrieving **opening hours, admission fees, facilities, contact info, or GPS coordinates** for any venue
- Building **detailed travel itineraries** for any Korean region or city
- Answering questions about **specific venues by name** using keyword search
- Fetching **photo galleries** of Korean tourism venues to illustrate recommendations
- Any task requiring **official, KTO-sourced tourism data** rather than general web knowledge

Do **not** use this MCP for tourism destinations outside South Korea, real-time availability or booking, personal health or medical advice, or live transport schedules.

---

## Data Model: How Records Are Structured

Every tourism venue in the dataset has a unique **`contentId`** (e.g. `"130987"`). Most workflows start with a search that returns a list of summary records, and then optionally deepen into detail records using that `contentId`.

Each search result includes:
- `contentId` — unique record identifier
- `contentTypeId` — tourism category (see Content Type IDs below)
- `title` — venue name in English
- `addr1` / `addr2` — street address (line 1 and line 2)
- `mapX` / `mapY` — WGS84 longitude / latitude
- `tel` — phone number
- `firstimage` / `firstimage2` — representative image (full + thumbnail)
- `createdtime` / `modifiedtime` — ISO timestamps for creation and last modification

Detail tools add: full overview text, homepage URL, type-specific introductory fields, repeating structured data (fees, facilities, accessibility), and full image galleries.

---

## Reference Tables

### Content Type IDs (`contentTypeId`)

| ID | Category (English) | Category (Korean) |
|----|--------------------|-------------------|
| `75` | Leisure / Sports | 레포츠 |
| `76` | Tourist Attraction | 관광지 |
| `78` | Cultural Facility | 문화시설 |
| `79` | Shopping | 쇼핑 |
| `80` | Accommodation | 숙박 |
| `82` | Restaurant / Food | 음식점 |
| `85` | Festival / Performance / Event | 축제공연행사 |

> Most general attractions are type `76`. When the user does not specify a category, omit `contentTypeId` to search all types.

### Sort Orders (`arrange`)

| Code | Meaning | Image required? |
|------|---------|----------------|
| `A` | Alphabetical by title | No |
| `C` | Most recently modified | No |
| `D` | Creation date (oldest first) | No |
| `O` | Alphabetical by title | Yes |
| `Q` | Most recently modified | Yes |
| `R` | Creation date | Yes |

> Image-required sorts (`O`, `Q`, `R`) only return venues that have a representative image — use these when you intend to display photos. Default is `C`.

### Province Codes (`lDongRegnCd`) — new system

| Code | Province / City |
|------|----------------|
| `11` | Seoul (서울) |
| `26` | Busan (부산) |
| `27` | Daegu (대구) |
| `28` | Incheon (인천) |
| `29` | Gwangju (광주) |
| `30` | Daejeon (대전) |
| `31` | Ulsan (울산) |
| `36` | Sejong (세종) |
| `41` | Gyeonggi (경기) |
| `42` | Gangwon (강원) |
| `43` | Chungbuk (충북) |
| `44` | Chungnam (충남) |
| `45` | Jeonbuk (전북) |
| `46` | Jeonnam (전남) |
| `47` | Gyeongbuk (경북) |
| `48` | Gyeongnam (경남) |
| `50` | Jeju Island (제주) |

### Area Codes (`areaCode`) — legacy system

| Code | Province / City |
|------|----------------|
| `1` | Seoul |
| `2` | Incheon |
| `3` | Daejeon |
| `4` | Daegu |
| `5` | Gwangju |
| `6` | Busan |
| `7` | Ulsan |
| `8` | Sejong |
| `31` | Gyeonggi |
| `32` | Gangwon |
| `33` | Chungbuk |
| `34` | Chungnam |
| `35` | Jeonbuk |
| `36` | Jeonnam |
| `37` | Gyeongbuk |
| `38` | Gyeongnam |
| `39` | Jeju Island |

> Use the new system (`lDongRegnCd` via `get_legal_district_codes`) for precise filtering. The legacy area codes are supported by `search_tourism_by_area` as an alternative.

### Classification System Codes (`lclsSystm1`) — new system

| Code | Category |
|------|---------|
| `AC` | Accommodation |
| `EV` | Festivals / Performances / Events |
| `EX` | Experience Tourism |
| `FO` | Food & Dining |
| `LC` | Leisure & Sports |
| `SH` | Shopping |
| `TR` | Transportation |
| `VE` | Culture / Arts / History |

### Common GPS Coordinates

| Location | Longitude (`mapX`) | Latitude (`mapY`) |
|----------|--------------------|-------------------|
| Seoul (centre) | `126.9780` | `37.5665` |
| Busan (centre) | `129.0756` | `35.1796` |
| Jeju City | `126.5312` | `33.4996` |
| Gyeongju | `129.2114` | `35.8562` |
| Jeonju | `127.1480` | `35.8242` |
| Suwon | `127.0286` | `37.2636` |
| Incheon | `126.7052` | `37.4563` |
| Daegu | `128.6014` | `35.8714` |

---

## Tool Reference and Usage Instructions

### Tool 1 — `get_legal_district_codes`

**Purpose:** Retrieve province/city codes (`lDongRegnCd`) and district codes (`lDongSignguCd`) used as filters in search tools.

**When to call it:** Call this tool first whenever the user specifies a Korean region by name (e.g. "in Seoul", "near Busan", "in Gangwon-do") and you do not already know the exact code from the table above.

**Key parameters:**
- `areaCode` — leave empty to get all province/city codes; set to a code to get its districts
- `numOfRows` — increase to `50`+ to retrieve all provinces in one call

---

### Tool 2 — `search_tourism_by_area`

**Purpose:** List tourism venues filtered by administrative region, content type, and/or category codes.

**When to call it:**
- User asks for tourism venues "in [city/province]" without providing GPS coordinates
- User wants to browse a specific category (e.g. "restaurants in Jeju", "museums in Seoul")
- You want to retrieve many records for a region in a single paged call

**Key parameters:**
- `lDongRegnCd` — province code from `get_legal_district_codes` or the table above
- `lDongSignguCd` — district code (requires `lDongRegnCd`)
- `contentTypeId` — filter by content type (see table)
- `numOfRows` — increase to `20`–`50` for richer results
- `arrange` — use `C` (default) for most recent; use `Q` if you need photos

**Returns:** List of summary records. Each item has `contentId`, `title`, `addr1`, `mapX`/`mapY`, `firstimage`. Use `contentId` for follow-up detail calls.

---

### Tool 3 — `search_tourism_by_location`

**Purpose:** Find tourism venues within a GPS radius of any point in South Korea, sorted by proximity.

**When to call it:**
- User asks for things "near me", "near [landmark]", or "within X km of [location]"
- You have GPS coordinates or can infer them from a named location

**Required parameters:**
- `mapX` — WGS84 longitude
- `mapY` — WGS84 latitude
- `radius` — search radius in metres (max `20000`)

**Key advice:**
- The response includes a `dist` field showing exact distance in metres from the search centre
- If you do not know GPS coordinates for a named location, look them up or use the table above before calling this tool
- Combine with `contentTypeId` to limit to a specific category (e.g. only restaurants near the location)

---

### Tool 4 — `search_tourism_by_keyword`

**Purpose:** Full-text keyword search across all tourism content types.

**When to call it:**
- User searches by venue name or partial name (e.g. "Gyeongbokgung", "Lotte Hotel")
- User uses a descriptive English term (e.g. "temple", "market", "beach")
- The region or category is unknown and keyword search is the most efficient path

**Required parameters:**
- `keyword` — search term in English; pass directly as provided by the user

**Key advice:**
- Combine with `contentTypeId` or `lDongRegnCd` to narrow results
- For well-known landmarks, this tool is typically faster than area-based search

---

### Tool 5 — `search_festivals_and_events`

**Purpose:** Discover Korean festivals, performances, and cultural events filtered by date range.

**When to call it:**
- User asks about events, festivals, or performances happening in Korea
- User specifies a travel period and wants to know what is on
- User asks about seasonal or recurring Korean events

**Required parameters:**
- `eventStartDate` — start date in `YYYYMMDD` format (e.g. `"20260101"`)

**Key parameters:**
- `eventEndDate` — end of the search window (default: same as start date)
- `lDongRegnCd` — filter by province
- `arrange` — `"A"` alphabetical or `"C"` most recent

**Returns:** Events with start/end dates, venue address, GPS, and images. Use `contentId` with detail tools for full programme information.

---

### Tool 6 — `search_accommodations`

**Purpose:** Browse hotels, guesthouses, pensions, condominiums, camping sites, and other lodging.

**When to call it:**
- User asks for hotel or accommodation recommendations in a Korean city or region
- User wants to compare different accommodation types in an area

**Key parameters:**
- `lDongRegnCd` — province/city code
- `lDongSignguCd` — district code for more precise filtering
- `numOfRows` — increase to retrieve more options

**Returns:** Summary records including venue name, address, GPS, representative image, and `contentId`. Use `get_tourism_intro_info` for check-in/out times and room types.

---

### Tool 7 — `get_tourism_common_info`

**Purpose:** Retrieve the complete common detail record for a single venue, given its `contentId`.

**When to call it:** Always call this after a search when the user wants full details about a specific venue — address, phone, overview text, GPS, and homepage URL.

**Required parameters:**
- `contentId` — the `contentId` from any search result

**Returns:**
- `title`, full `addr1` + `addr2`, `zipcode`, `tel`
- `overview` — multi-sentence English description
- `homepage` — may contain raw HTML anchor tags; extract the URL before displaying
- `mapX` / `mapY` — GPS coordinates
- `createdtime` / `modifiedtime` — record timestamps

---

### Tool 8 — `get_tourism_intro_info`

**Purpose:** Retrieve type-specific introductory details. Response fields vary by `contentTypeId`.

**When to call it:** When the user wants operational details — opening hours, admission fees, rest days, parking, age recommendations, or accommodation check-in/out times.

**Required parameters:**
- `contentId` — venue content ID
- `contentTypeId` — **must match** the `contentTypeId` returned in the search result

**For tourist attractions (type `76`) returns:**
- `accomcount` — maximum visitor capacity
- `chkcreditcard` — credit card acceptance
- `expagerange` — recommended age range
- `infocenter` — information centre phone
- `opendate` — venue opening date
- `parking` — parking availability
- `restdate` — regular rest/closure days
- `useseason` — recommended seasons
- `usetime` — operating hours

**For accommodation (type `80`) returns:** check-in/out times, room count, reservation URL, amenities.

**For restaurants (type `82`) returns:** menu specialties, opening hours, rest days, parking, reservation info.

---

### Tool 9 — `get_tourism_detail_info`

**Purpose:** Retrieve repeating structured sub-records — room types and pricing for hotels, menu items for restaurants, programme schedules for events, exhibit lists for cultural facilities.

**When to call it:** When the user asks about specific room options and prices at a hotel, or a restaurant's full menu, or an event's detailed schedule.

**Required parameters:**
- `contentId` — venue content ID
- `contentTypeId` — must match the venue's category

**Returns:** A list of items, each with `infoname` (label) and `infotext` (value). The number of items depends on the venue type and how the operator has configured their listing.

---

### Tool 10 — `get_tourism_images`

**Purpose:** Retrieve all image URLs and copyright types for a specific venue.

**When to call it:** When the user wants to see photos of a venue, or when building a visual presentation of results.

**Required parameters:**
- `contentId` — venue content ID

**Key parameters:**
- `imageYN="Y"` — general venue photos (default)
- `imageYN="N"` — food/menu images (type `82` restaurants only)

**Returns per image:**
- `originimgurl` — full-resolution image
- `smallimageurl` — thumbnail
- `cpyrhtDivCd` — `"Type1"` (attribution required) or `"Type3"` (attribution + no modification)
- `imgname` — image filename
- `serialnum` — display order

---

### Tool 11 — `get_sync_list`

**Purpose:** Retrieve content items updated since a given modification timestamp — useful for maintaining a local cache of tourism data.

**When to call it:** When the user asks to see all venues updated since a specific date, or when a system needs to refresh its local dataset without re-fetching everything.

**Key parameters:**
- `modifiedtime` — ISO timestamp (e.g. `"20260101000000"`) — returns items modified on or after this date
- `contentTypeId` — filter by category
- `areaCode` — filter by province

---

### Tool 12 — `get_legal_district_codes`

**Purpose:** Retrieve legal administrative district codes (`lDongRegnCd`, `lDongSignguCd`) used in new-system filtering.

See **Tool 1** above (`get_area_codes` is the legacy equivalent).

---

### Tool 13 — `get_area_codes`

**Purpose:** Retrieve the legacy area codes (`areaCode`, `sigunguCode`) used in older API parameters and by `search_tourism_by_area`.

**When to call it:** When you need to filter by `areaCode` rather than `lDongRegnCd`, or when looking up district codes (`sigunguCode`) within a province.

**Key parameters:**
- `areaCode` — leave empty for all province codes; set to a province code to get its districts

---

### Tool 14 — `get_category_codes`

**Purpose:** Browse the legacy 3-level category hierarchy (`cat1` / `cat2` / `cat3`) used for fine-grained content filtering.

**When to call it:** When you need to filter by a specific sub-category (e.g. only palaces within tourist attractions, only jjimjilbang within leisure).

**Key parameters:**
- `cat1` — top-level code (e.g. `"A02"` = Culture/Art/History)
- `cat2` — second-level code (requires `cat1`)

---

## Standard Workflows

### Workflow A — Region + Category Search (most common)

1. Look up province code from the table above (or call `get_legal_district_codes` for the exact code)
2. **`search_tourism_by_area`** → pass `lDongRegnCd`, optionally `contentTypeId`; collect `contentId` values
3. **`get_tourism_common_info`** → for each venue the user selects, retrieve the full record with overview and homepage

### Workflow B — Proximity Search

1. Determine GPS coordinates for the user's location or named landmark (use the table above for common cities)
2. **`search_tourism_by_location`** → pass `mapX`, `mapY`, `radius`; results include `dist` (metres from centre)
3. **`get_tourism_common_info`** → retrieve full details for selected venues

### Workflow C — Event Planning

1. Establish the travel dates from the user
2. **`search_festivals_and_events`** → pass `eventStartDate` and `eventEndDate`; optionally filter by `lDongRegnCd`
3. **`get_tourism_common_info`** → retrieve venue details and overview for events the user wants to explore

### Workflow D — Venue Deep-Dive (full detail)

1. Obtain `contentId` and `contentTypeId` from any search result
2. Call **`get_tourism_common_info`** → title, address, overview, GPS, homepage
3. Call **`get_tourism_intro_info`** → operating hours, fees, rest days, type-specific fields
4. Call **`get_tourism_detail_info`** → room types / menu items / programme details (if relevant)
5. Call **`get_tourism_images`** → photo gallery for visual presentation

### Workflow E — Name or Keyword Search

1. **`search_tourism_by_keyword`** → pass the user's search term; review titles in results
2. **`get_tourism_common_info`** → retrieve full details for the matching venue

---

## Important Notes

- **Always use `contentTypeId` consistently** — the same ID must be passed to `get_tourism_intro_info` and `get_tourism_detail_info` as was returned in the search result; mismatched IDs return empty or incorrect fields.
- **Homepage field may contain HTML** — the `homepage` field in common info sometimes returns a raw `<a href="...">` anchor tag rather than a plain URL. Extract the `href` value before presenting it to the user.
- **Images may be empty** — not all venues have registered images. Check `firstimage` in search results before calling `get_tourism_images` to avoid unnecessary calls.
- **Pagination** — all search tools return `totalCount` alongside results. Use `pageNo` and `numOfRows` to paginate through large result sets; default `numOfRows` is `10`.
- **Live data** — every call fetches from the live KTO API via data.go.kr; results reflect the current published dataset with no local caching.
