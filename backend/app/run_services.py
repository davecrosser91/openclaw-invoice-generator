# 📄 start_all_services.py
import subprocess
import logging

# Absoluter oder relativer Pfad zu deinen drei Skripten
scripts = [
    "src/docgen_services/hocr_service.py",
    "src/docgen_services/mock_service.py",
    "src/docgen_services/api_service.py",
]
processes = []

try:
    for script in scripts:
        logging.info(f"🚀 Starte {script} ...")
        proc = subprocess.Popen(["uv", "run", "--no-sync", script])
        processes.append(proc)

    # Warten bis alle Prozesse fertig sind (oder mit Ctrl+C beendet werden)
    for proc in processes:
        proc.wait()

except KeyboardInterrupt:
    logging.info("🛑 Abbruch - beende alle Prozesse ...")
    for proc in processes:
        proc.terminate()
