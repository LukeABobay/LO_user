# /dat1/bobayl/LO_user/extract/box/run_extractions_and_stage.py

import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
start_date = datetime(2019, 1, 1)
end_date = datetime(2019, 4, 30)
gtx = "cas7_t0_x4b"
roms_out_num = "1"
job = "bobay"
list_type = "lowpass"
surf = "False"
uv_to_rho = "True"
script = "/dat1/bobayl/LO/extract/box/extract_box_chunks.py"
tmp_dir = Path("/home/bobayl/tmp_lo_transfer")
tmp_dir.mkdir(parents=True, exist_ok=True)

# Loop over each month
curr = start_date
while curr <= end_date:
    ds0 = curr.strftime("%Y.%m.%d")
    next_month = (curr.replace(day=28) + timedelta(days=4)).replace(day=1)
    ds1_dt = min(end_date, next_month - timedelta(days=1))
    ds1 = ds1_dt.strftime("%Y.%m.%d")

    print(f"\n>>> Extracting {ds0} to {ds1}")

    # Run extract_box_chunks.py
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
        print(f"  ✘ Extraction failed for {ds0} to {ds1}")
        curr = next_month
        continue

    # Move output file to tmp directory
    box_subdir = f"{job}_{ds0}_{ds1}_chunks"
    filename = f"{job}_{ds0}_{ds1}.nc"
    src = Path(f"/dat1/bobayl/LO_output/extract/{gtx}/box/{box_subdir}/{filename}")
    dst = tmp_dir / filename

    if src.exists():
        print(f"  → Moving {filename} to {dst}")
        dst.write_bytes(src.read_bytes())
    else:
        print(f"  ✘ Output file not found: {src}")

    curr = next_month

Path("/home/bobayl/tmp_lo_transfer/extraction.done").touch()
print("✔ All extractions completed. Flag file created.")
