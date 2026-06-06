# Fieldbook

Personal Pokemon GO trainer archive. Visualises data exported from Niantic's GDPR data portal as a single self-contained HTML file — no build step, no server required.

## Running locally

Open `index.html` directly in a browser, or serve it with Python to avoid any local file-origin restrictions with Leaflet tiles:

```sh
python3 -m http.server 8080
# then open http://localhost:8080
```

## What's inside

| Tab | Content |
|---|---|
| Activity | Leaflet map of 269 encounter locations, monthly encounter and pokestop spin charts |
| Collection | Searchable grid of 1,110 Pokemon in storage |
| Pokédex | Placeholder |
| Spending | Real-money purchase history by currency (NZD, CAD, GBP) |

## Dependencies (CDN)

- [Chart.js 4.4.0](https://www.chartjs.org/)
- [Leaflet 1.9.4](https://leafletjs.com/)
- [Leaflet.markercluster 1.5.3](https://github.com/Leaflet/Leaflet.markercluster)
- [Lato](https://fonts.google.com/specimen/Lato) via Google Fonts

## Data source

Data comes from a Niantic GDPR export (zip of TSVs/CSVs), pre-processed with Python into a JSON blob embedded directly in `index.html`.

## Privacy note

`index.html` contains personal data including approximate encounter coordinates and full purchase history. Do not share the file publicly or commit it to a public repository without stripping the `DATA` blob first.
