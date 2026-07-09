# /dat1/bobayl/LO_user/extract/box/run_extractions_and_stage.py

import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
isiis_dates = [
    "2022-03-06",
    "2022-03-07",
    "2022-03-08",
    "2022-03-09",
    "2022-03-10",
    "2022-03-12",
    "2022-07-21",
    "2022-07-22",
    "2022-07-23",
    "2022-07-24",
    "2022-07-25",
    "2022-07-26",
    "2022-07-27",
    "2022-07-28",
    "2023-02-17",
    "2023-02-18",
    "2023-02-20",
    "2023-02-24",
    "2023-02-25",
    "2023-02-26",
    "2023-08-11",
    "2023-08-12",
    "2023-08-13",
    "2023-08-14",
    "2023-08-15",
    "2023-08-16",
    "2023-08-17",
    "2023-08-20",
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

# Loop over each date with ISIIS NBSS observations.
for isiis_date in isiis_dates:
    curr = datetime.strptime(isiis_date, "%Y-%m-%d")
    ds0 = curr.strftime("%Y.%m.%d")
    ds1 = ds0
    filename = f"{job}_{ds0}_{ds1}.nc"
    dst = tmp_dir / filename

    print(f"\n>>> Extracting {ds0} to {ds1}")

    if dst.exists():
        print(f"  -> {filename} is already staged at {dst}. Skipping.")
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
        continue

    box_subdir = f"{job}_{ds0}_{ds1}_chunks"
    src = Path(f"/dat1/bobayl/LO_output/extract/{gtx}/box/{box_subdir}/{filename}")

    if src.exists():
        print(f"  -> Moving {filename} to {dst}")
        dst.write_bytes(src.read_bytes())
    else:
        print(f"  x Output file not found: {src}")

Path("/home/bobayl/tmp_lo_transfer/extraction.done").touch()
print("All extractions completed. Flag file created.")
