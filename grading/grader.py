import os
import json
import subprocess
import csv
import datetime
import sys

print("🚀 Memulai Auto Grading...")

# =============================
# 1️⃣ DETEKSI FOLDER TUGAS
# =============================

folders = [f for f in os.listdir('.') if f.startswith("tugas-")]

if not folders:
    print("❌ Tidak ada folder tugas ditemukan.")
    sys.exit(1)

active_tugas = folders[0]
print(f"📁 Tugas aktif terdeteksi: {active_tugas}")

# =============================
# 2️⃣ LOAD CONFIG
# =============================

config_path = "grading/config.json"

if not os.path.exists(config_path):
    print("❌ config.json tidak ditemukan.")
    sys.exit(1)

with open(config_path) as f:
    config = json.load(f)

if active_tugas not in config:
    print("❌ Konfigurasi untuk tugas ini tidak ditemukan.")
    sys.exit(1)

rules = config[active_tugas]

# =============================
# 3️⃣ CEK COMMIT
# =============================

commit_score = 0
try:
    commit_count = int(subprocess.check_output(
        ["git", "rev-list", "--count", "HEAD"]).decode().strip())
except:
    commit_count = 0

print(f"🔢 Jumlah commit: {commit_count}")

if commit_count >= rules["min_commit"]:
    commit_score = rules["weight_commit"]

# =============================
# 4️⃣ CEK STRUKTUR FOLDER
# =============================

structure_score = 0

if os.path.exists(active_tugas):
    structure_score = rules["weight_structure"]

# =============================
# 5️⃣ JALANKAN UNIT TEST DINAMIS
# =============================

test_score = 0

test_path = f"tests/{active_tugas}"

if os.path.exists(test_path):
    result = subprocess.run(
        ["pytest", test_path, "--tb=short"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if result.returncode == 0:
        test_score = rules["weight_test"]
else:
    print("⚠ Folder test tidak ditemukan.")

# =============================
# 6️⃣ HITUNG TOTAL
# =============================

total = commit_score + structure_score + test_score

print("===================================")
print(f"Commit Score    : {commit_score}")
print(f"Structure Score : {structure_score}")
print(f"Test Score      : {test_score}")
print(f"🎯 TOTAL SCORE  : {total}")
print("===================================")

# =============================
# 7️⃣ EXPORT CSV
# =============================

os.makedirs("reports", exist_ok=True)

csv_path = "reports/grade.csv"

with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Tanggal", "Tugas", "Commit", "Struktur", "Test", "Total"])
    writer.writerow([
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        active_tugas,
        commit_score,
        structure_score,
        test_score,
        total
    ])

print(f"📄 Laporan disimpan di {csv_path}")

# =============================
# 8️⃣ KIRIM OUTPUT KE GITHUB ACTIONS (FORMAT BARU)
# =============================

github_output = os.environ.get("GITHUB_OUTPUT")

if github_output:
    with open(github_output, "a") as f:
        f.write(f"total={total}\n")

# =============================
# 9️⃣ FAIL JIKA NILAI < 50
# =============================

if total < 50:
    print("❌ Nilai di bawah standar. Gagal.")
    sys.exit(1)

print("✅ Grading selesai dengan sukses.")
