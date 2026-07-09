# /dat1/bobayl/LO_user/extract/box/run_extractions_and_stage.py

import subprocess
from pathlib import Path

# Configuration
isiis_months = [
    ("2022.03.01", "2022.03.31"),
    ("2022.07.01", "2022.07.31"),
    ("2023.02.01", "2023.02.28"),
    ("2023.08.01", "2023.08.31"),
]
gtx = "cas7_t0_x4b"
roms_out_num = "1"
job = "bobay"
list_type = "lowpass"
surf = "False"
uv_to_rho = "True"
script = "/dat1/bobayl/LO/extract/box/extract_box_chunks.py"
tmp_dir = Path("/home/bobayl/tmp_lo_transfer")
tmp_dir.mkdir(parents=True, exist_ok=True)

n_success = 0
n_failed = 0
n_skipped = 0

# Loop over full months that contain ISIIS NBSS observations.
for ds0, ds1 in isiis_months:
    filename = f"{job}_{ds0}_{ds1}.nc"
    dst = tmp_dir / filename

    print(f"\n>>> Extracting {ds0} to {ds1}")

    if dst.exists():
        print(f"  -> {filename} is already staged at {dst}. Skipping.")
        n_skipped += 1
        continue

    result = subprocess.run([
        "python", script,
        "-gtx", gtx,
        "-ro", roms_out_num,
        "-lt", list_type,
        "-0", ds0,
        "-1", ds1,
        "-job", job,
        "-surf", surf,
        "-uv_to_rho", uv_to_rho
    ])

    if result.returncode != 0:
        print(f"  x Extraction failed for {ds0} to {ds1}")
        n_failed += 1
        continue

    box_subdir = f"{job}_{ds0}_{ds1}_chunks"
    src = Path(f"/dat1/bobayl/LO_output/extract/{gtx}/box/{box_subdir}/{filename}")

    if src.exists():
        print(f"  -> Moving {filename} to {dst}")
        dst.write_bytes(src.read_bytes())
        n_success += 1
    else:
        print(f"  x Output file not found: {src}")
        n_failed += 1

Path("/home/bobayl/tmp_lo_transfer/extraction.done").touch()
print(
    "All extractions completed. "
    f"Successful: {n_success}; skipped: {n_skipped}; failed: {n_failed}. "
    "Flag file created."
)
