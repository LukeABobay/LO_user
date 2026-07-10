# /home/bobayl/LO_user/extract/box/run_extractions_and_stage.py

import calendar
import os
import shutil
import subprocess
import time
from datetime import date
from pathlib import Path


# Configuration ------------------------------------------------------------

START_MONTH = os.environ.get("LIVE_OCEAN_START_MONTH", "2013-01")
END_MONTH = os.environ.get("LIVE_OCEAN_END_MONTH", "2025-12")

GTX = os.environ.get("LIVE_OCEAN_GTX", "cas7_t0_x4b")
ROMS_OUT_NUM = os.environ.get("LIVE_OCEAN_ROMS_OUT_NUM", "1")
JOB = os.environ.get("LIVE_OCEAN_JOB", "bobay")
LIST_TYPE = os.environ.get("LIVE_OCEAN_LIST_TYPE", "lowpass")
SURF = os.environ.get("LIVE_OCEAN_SURF", "False")
UV_TO_RHO = os.environ.get("LIVE_OCEAN_UV_TO_RHO", "True")
NPROC = os.environ.get("LIVE_OCEAN_NPROC", "10")

DEFAULT_LO_ROOT = Path("/dat1/bobayl/LO")
if not DEFAULT_LO_ROOT.exists():
    DEFAULT_LO_ROOT = Path("/home/bobayl/LO")
LO_ROOT = Path(os.environ.get("LIVE_OCEAN_LO_ROOT", str(DEFAULT_LO_ROOT)))
EXTRACT_SCRIPT = LO_ROOT / "extract" / "box" / "extract_box_chunks.py"

DEFAULT_LO_OUTPUT_ROOT = Path("/dat1/bobayl/LO_output")
if not DEFAULT_LO_OUTPUT_ROOT.exists():
    DEFAULT_LO_OUTPUT_ROOT = Path("/home/bobayl/LO_output")
LO_OUTPUT_ROOT = Path(os.environ.get("LIVE_OCEAN_LO_OUTPUT_ROOT", str(DEFAULT_LO_OUTPUT_ROOT)))

STAGE_DIR = Path(os.environ.get("LIVE_OCEAN_STAGE_DIR", "/home/bobayl/tmp_lo_transfer"))
MAX_STAGED_FILES = int(os.environ.get(
    "LIVE_OCEAN_MAX_STAGED_FILES",
    os.environ.get("MAX_STAGED_FILES", "4"),
))
WAIT_SECONDS = int(os.environ.get(
    "LIVE_OCEAN_WAIT_SECONDS",
    os.environ.get("STAGE_WAIT_SECONDS", "60"),
))
STOP_ON_FAILURE = os.environ.get("LIVE_OCEAN_STOP_ON_FAILURE", "True").lower() == "true"

DONE_FLAG = STAGE_DIR / "extraction.done"
FAILED_FLAG = STAGE_DIR / "extraction.failed"
STATUS_LOG = STAGE_DIR / "extraction_status.tsv"


# Helpers ------------------------------------------------------------------

def parse_month(month_string):
    year_string, month_string = month_string.split("-")
    return int(year_string), int(month_string)


def month_ranges(start_month, end_month):
    start_year, start_mon = parse_month(start_month)
    end_year, end_mon = parse_month(end_month)

    year = start_year
    month = start_mon
    while (year, month) <= (end_year, end_mon):
        last_day = calendar.monthrange(year, month)[1]
        yield (
            date(year, month, 1).strftime("%Y.%m.%d"),
            date(year, month, last_day).strftime("%Y.%m.%d"),
        )
        month += 1
        if month == 13:
            month = 1
            year += 1


def staged_nc_files():
    return sorted(STAGE_DIR.glob(f"{JOB}_*.nc"))


def wait_for_stage_space():
    while len(staged_nc_files()) >= MAX_STAGED_FILES:
        staged_names = ", ".join(path.name for path in staged_nc_files())
        print(
            f"Stage directory has {len(staged_nc_files())} completed files "
            f"(limit {MAX_STAGED_FILES}). Waiting {WAIT_SECONDS} s for Novus pull. "
            f"Files: {staged_names}",
            flush=True,
        )
        time.sleep(WAIT_SECONDS)


def write_status(ds0, ds1, filename, status, message=""):
    header_needed = not STATUS_LOG.exists()
    with STATUS_LOG.open("a", encoding="utf-8") as log:
        if header_needed:
            log.write("ds0\tds1\tfilename\tstatus\tmessage\n")
        clean_message = str(message).replace("\t", " ").replace("\n", " ")
        log.write(f"{ds0}\t{ds1}\t{filename}\t{status}\t{clean_message}\n")


def mark_failure(message):
    FAILED_FLAG.write_text(str(message) + "\n", encoding="utf-8")


def extraction_output_path(ds0, ds1, filename):
    box_subdir = f"{JOB}_{ds0}_{ds1}_chunks"
    return LO_OUTPUT_ROOT / "extract" / GTX / "box" / box_subdir / filename


def extract_month(ds0, ds1):
    cmd = [
        "python", str(EXTRACT_SCRIPT),
        "-gtx", GTX,
        "-ro", ROMS_OUT_NUM,
        "-lt", LIST_TYPE,
        "-0", ds0,
        "-1", ds1,
        "-job", JOB,
        "-surf", SURF,
        "-uv_to_rho", UV_TO_RHO,
        "-Nproc", NPROC,
    ]
    print("Running: " + " ".join(cmd), flush=True)
    return subprocess.run(cmd)


# Main ---------------------------------------------------------------------

STAGE_DIR.mkdir(parents=True, exist_ok=True)
DONE_FLAG.unlink(missing_ok=True)
FAILED_FLAG.unlink(missing_ok=True)

if not EXTRACT_SCRIPT.exists():
    message = f"Extractor not found: {EXTRACT_SCRIPT}"
    mark_failure(message)
    raise SystemExit(message)

n_success = 0
n_failed = 0
n_skipped = 0

try:
    for ds0, ds1 in month_ranges(START_MONTH, END_MONTH):
        filename = f"{JOB}_{ds0}_{ds1}.nc"
        dst = STAGE_DIR / filename
        partial_dst = STAGE_DIR / f".{filename}.partial"

        print(f"\n>>> Extracting {ds0} to {ds1}", flush=True)
        wait_for_stage_space()

        if dst.exists():
            print(f"  -> {filename} is already staged at {dst}. Skipping.", flush=True)
            write_status(ds0, ds1, filename, "skipped_already_staged")
            n_skipped += 1
            continue

        result = extract_month(ds0, ds1)
        if result.returncode != 0:
            message = f"Extraction failed for {ds0} to {ds1} with return code {result.returncode}"
            print(f"  x {message}", flush=True)
            write_status(ds0, ds1, filename, "failed", message)
            n_failed += 1
            if STOP_ON_FAILURE:
                mark_failure(message)
                raise SystemExit(result.returncode)
            continue

        src = extraction_output_path(ds0, ds1, filename)
        if not src.exists():
            message = f"Output file not found: {src}"
            print(f"  x {message}", flush=True)
            write_status(ds0, ds1, filename, "failed_missing_output", message)
            n_failed += 1
            if STOP_ON_FAILURE:
                mark_failure(message)
                raise SystemExit(1)
            continue

        partial_dst.unlink(missing_ok=True)
        print(f"  -> Staging {filename} to {dst}", flush=True)
        shutil.move(str(src), str(partial_dst))
        partial_dst.replace(dst)
        write_status(ds0, ds1, filename, "staged")
        n_success += 1

except BaseException as e:
    if not FAILED_FLAG.exists() and not isinstance(e, KeyboardInterrupt):
        mark_failure(e)
    raise
else:
    DONE_FLAG.touch()
    print(
        "All extractions completed. "
        f"Successful: {n_success}; skipped: {n_skipped}; failed: {n_failed}. "
        "Flag file created.",
        flush=True,
    )
