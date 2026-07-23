import json
from pathlib import Path
from typing import Any

BASE_DATASET_DIR = Path("data/benchmarks")

def save_dataset_artifact(
        case_id: str,
        artifact_name: str,
        data: Any,
) -> Path:
    case_directory = BASE_DATASET_DIR / case_id
    case_directory.mkdir(parents=True, exist_ok=True)
    file_path = case_directory / f"{artifact_name}.json"
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )
    return file_path
def save_benchmark_case(
        case_id: str,
        input_data: Any,
        vervotech_response: Any,
        our_response: Any,
) -> dict[str, Path]:
    input_path = save_dataset_artifact(
        case_id=case_id,
        artifact_name="input",
        data=input_data,
    )

    vervotech_path = save_dataset_artifact(
        case_id=case_id,
        artifact_name="vervotech",
        data=vervotech_response,
    )

    our_path = save_dataset_artifact(
        case_id=case_id,
        artifact_name="our_v4",
        data=our_response,
    )

    return {
        "input": input_path,
        "vervotech": vervotech_path,
        "our_v4": our_path,
    }

def load_json_file(file_path: Path)-> Any:
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)
    
def load_benchmark_case(case_id: str)-> dict[str, Any]:
    case_directory = BASE_DATASET_DIR / case_id

    if not case_directory.exists():
        raise FileNotFoundError(
            f"Benchmark case '{case_id}' does not exists"
        )
    return{
        "input": load_json_file(case_directory / "input.json"),
        "vervotech": load_json_file(case_directory / "vervotech.json"),
        "our_v4": load_json_file(case_directory / "our_v4.json"),
    }

