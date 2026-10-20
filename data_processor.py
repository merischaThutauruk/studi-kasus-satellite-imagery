import json
import math
import random


class SatelliteDataProcessor:

  def __init__(self, region_bounds=None):
    """Inisialisasi prosesor data satelit dengan batas wilayah (Bounding Box)."""
    self.regions = ["Kalimantan", "Sumatera", "Papua", "Sulawesi"]
    self.bounds = region_bounds or {
        "lat_min": -11.0,
        "lat_max": 6.0,
        "lon_min": 95.0,
        "lon_max": 141.0,
    }

  def process_multisensor_stack(self, n_records=50):
    """
    Mensimulasikan tumpukan data multi-band dari satelit radar (Sentinel-1 SAR)
    dan optik (Sentinel-2) lengkap dengan koordinat geospasial tiruan.
    """
    random.seed(42)
    raw_data = []

    for i in range(n_records):
      if i % 10 == 0:
        lat = random.uniform(-95.0, 95.0) 
        lon = random.uniform(200.0, 250.0)  
      else:
        lat = random.uniform(self.bounds["lat_min"], self.bounds["lat_max"])
        lon = random.uniform(self.bounds["lon_min"], self.bounds["lon_max"])

      record = {
          "id_alert": f"ALT-2026-{1000 + i}",
          "wilayah": random.choice(self.regions),
          "latitude": round(lat, 6),
          "longitude": round(lon, 6),
          "sentinel_1_sar": round(
              random.uniform(0.1, 0.9), 4
          ),  
          "sentinel_2_optik": round(
              random.uniform(0.2, 0.95), 4
          ),
          "luas_gangguan_ha": round(random.uniform(5.0, 150.0), 2),
      }
      raw_data.append(record)

    return raw_data

  def validate_and_clean_spatial_data(self, raw_data):
    """
    Melakukan proses Spatial Cleaning: menyaring data dengan koordinat
    yang berada di luar batas teritorial wilayah studi yang sah.
    """
    valid_records = []
    invalid_count = 0

    for record in raw_data:
      lat = record["latitude"]
      lon = record["longitude"]

      if (self.bounds["lat_min"] <= lat <= self.bounds["lat_max"]) and (
          self.bounds["lon_min"] <= lon <= self.bounds["lon_max"]
      ):
        valid_records.append(record)
      else:
        invalid_count += 1

    print(f"[INFO] Total data mentah masuk       : {len(raw_data)}")
    print(f"[INFO] Data berhasil divalidasi      : {len(valid_records)}")
    print(f"[INFO] Data invalid dibuang          : {invalid_count}")
    return valid_records

  def calculate_regional_statistics(self, valid_data):
    """
    Menghitung rekapitulasi statistik kerusakan hutan per wilayah
    menggunakan fungsi agregasi berbasis kamus (dictionary) Python murni.
    """
    stats = {}

    for item in valid_data:
      wilayah = item["wilayah"]
      luas = item["luas_gangguan_ha"]

      if wilayah not in stats:
        stats[wilayah] = {"total_kejadian": 0, "total_luas_ha": 0.0}

      stats[wilayah]["total_kejadian"] += 1
      stats[wilayah]["total_luas_ha"] += luas

    for wilayah in stats:
      total_kejadian = stats[wilayah]["total_kejadian"]
      total_luas = stats[wilayah]["total_luas_ha"]
      stats[wilayah]["rata_rata_luas_ha"] = round(total_luas / total_kejadian, 2)
      stats[wilayah]["total_luas_ha"] = round(total_luas, 2)

    return stats

  def export_to_geojson_format(self, valid_data, filename="output_spatial.geojson"):
    """Mengonversi data spasial yang bersih ke dalam format standar GeoJSON."""
    features = []
    for item in valid_data:
      feature = {
          "type": "Feature",
          "geometry": {
              "type": "Point",
              "coordinates": [item["longitude"], item["latitude"]],
          },
          "properties": {
              "id_alert": item["id_alert"],
              "wilayah": item["wilayah"],
              "sentinel_1_sar": item["sentinel_1_sar"],
              "sentinel_2_optik": item["sentinel_2_optik"],
              "luas_gangguan_ha": item["luas_gangguan_ha"],
          },
      }
      features.append(feature)

    geojson_collection = {"type": "FeatureCollection", "features": features}

    with open(filename, "w", encoding="utf-8") as f:
      json.dump(geojson_collection, f, indent=4)

    print(
        f"[SUKSES] Berhasil mengekspor {len(features)} objek spasial ke file"
        f" '{filename}'."
    )

if __name__ == "__main__":
  processor = SatelliteDataProcessor()

  print("=== 1. MENJALANKAN SIMULASI DATA MULTI-SENSOR ===")
  data_mentah = processor.process_multisensor_stack(n_records=40)

  print("\n=== 2. VALIDASI & SPATIAL CLEANING ===")
  data_bersih = processor.validate_and_clean_spatial_data(data_mentah)

  print("\n=== 3. STATISTIK RINGKASAN REGIONAL ===")
  statistik = processor.calculate_regional_statistics(data_bersih)
  for wil, val in statistik.items():
    print(
        f" - {wil}: {val['total_kejadian']} Kasus | Total Luas:"
        f" {val['total_luas_ha']} Ha | Rata-rata: {val['rata_rata_luas_ha']} Ha"
    )

  print("\n=== 4. EKSPOR FORMAT SPASIAL GEOJSON ===")
  processor.export_to_geojson_format(data_bersih, "simulasi_hutan.geojson")