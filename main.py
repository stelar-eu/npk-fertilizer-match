import json
import sys
import traceback
from utils.mclient import MinioClient
import pandas as pd
import os
import tempfile

REQUIRED_COLUMNS = {"N", "P", "K"}

def npk_distance(npk1, npk2):
    """Euclidean distance between two N‑P‑K triples."""
    return sum((a - b) ** 2 for a, b in zip(npk1, npk2)) ** 0.5

def match_fertilizers(df_npk: pd.DataFrame, df_fert: pd.DataFrame) -> pd.DataFrame:
    """Attach the closest‑match fertilizer (by N‑P‑K composition) to every user row."""

    # Guard: validate schema
    if not (REQUIRED_COLUMNS <= set(df_npk.columns) and REQUIRED_COLUMNS <= set(df_fert.columns)):
        raise ValueError(f"Both CSVs must contain columns {REQUIRED_COLUMNS}.")

    result = df_npk.copy()
    result["Fertilizzante"] = ""

    # Pre‑extract fertilizer tuples once for speed
    fert_tuples = [((row.N, row.P, row.K), row.Nome) for _, row in df_fert.iterrows()]

    for idx, row in result.iterrows():
        user_npk = (row.N, row.P, row.K)
        # Find best match
        best = min(fert_tuples, key=lambda tpl: npk_distance(user_npk, tpl[0]))
        result.at[idx, "Fertilizzante"] = best[1]

    return result


def run(json: dict):

    try:
        # --------------- MinIO initialisation ---------------
        minio_cfg = json.get("minio", {})
        mc = MinioClient(
            minio_cfg.get("endpoint_url"),
            minio_cfg.get("id"),
            minio_cfg.get("key"),
            secure=True,
            session_token=minio_cfg.get("skey"),
        )

        # --------------- Retrieve user parameters -----------
        inputs = json["input"]
        outputs = json["output"]

        npk_remote_path = inputs["npk_values"][0]
        fert_remote_path = inputs["fertilizer_dataset"][0]
        output_remote_path = outputs["matched_fertilizers"]

        # ---------------- IO: download inputs ----------------
        with tempfile.TemporaryDirectory() as tmpdir:
            local_npk = os.path.join(tmpdir, "npk.csv")
            local_fert = os.path.join(tmpdir, "fert.csv")

            mc.get_object(s3_path=npk_remote_path, local_path=local_npk)
            mc.get_object(s3_path=fert_remote_path, local_path=local_fert)

            # ---------------- Core logic --------------------
            df_npk = pd.read_csv(local_npk)
            df_fert = pd.read_csv(local_fert)
            df_out = match_fertilizers(df_npk, df_fert)

            local_out = os.path.join(tmpdir, "matched.csv")
            df_out.to_csv(local_out, index=False)

            # --------------- Upload result ------------------
            mc.put_object(s3_path=output_remote_path, file_path=local_out)

        # --------------- Build response ---------------------
        return {
            "message": "Tool executed successfully!",
            "output": {
                "matched_fertilizers": output_remote_path,
            },
            "metrics": {
                "records_in": len(df_npk),
                "records_out": len(df_out),
            },
            "status": "success",
        }

    except Exception:
        print(traceback.format_exc())
        return {
            "message": "An error occurred during fertilizer matching.",
            "error": traceback.format_exc(),
            "status": "error",
        }

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise ValueError("Please provide 2 files.")
    with open(sys.argv[1]) as o:
        j = json.load(o)
    response = run(j)
    with open(sys.argv[2], 'w') as o:
        o.write(json.dumps(response, indent=4))