import os
import json
import subprocess
import csv
import datetime

# Ambil folder tugas aktif
folders = [f for f in os.listdir('.') if f.startswith("tugas-")]

if not folders:
    print("Tidak ada folder tugas ditemukan")
    exit(1)

active_tugas = folders[0]

with open("grading/config.json") as f:
    config = json.load(f)

if active_tugas not in config:
    print("Konfigurasi tidak ditemukan")
    exit(1)

rules = config[active_tugas]

# =============================
# 1️⃣ CEK COMMIT
# =============================
commit_count = int(subprocess.check_output(
    ["git", "rev-list", "--count", "HEAD"]).decode().strip())

commit_score = 0
if commit_count >= rules["min_commit"]:
    commit_score = rules["weight_commit"]

# =============================
# 2️⃣ CEK STRUKTUR
# =============================
structure_score = 0
if os.path.exists(active_tugas):
    structure_score = rules["weight_structure"]

# =============================
# 3️⃣ RUN TEST
# =============================
result = subprocess.run(
    ["pytest", f"tests/{active_tugas}"],
    capture_output=True
)

test_score = 0
if result.returncode == 0:
    test_score = rules["weight_test"]

# =============================
# TOTAL NILAI
# =============================
total = commit_score + structure_score + test_score

print("Commit Score:", commit_score)
print("Structure Score:", structure_score)
print("Test Score:", test_score)
print("Total Score:", total)

# =============================
# EXPORT CSV
# =============================
os.makedirs("reports", exist_ok=True)

with open("reports/grade.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Tanggal", "Tugas", "Commit", "Struktur", "Test", "Total"])
    writer.writerow([
        datetime.datetime.now(),
        active_tugas,
        commit_score,
        structure_score,
        test_score,
        total
    ])

if total < 50:
    exit(1)
