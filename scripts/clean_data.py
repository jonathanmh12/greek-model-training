import os
import glob
from lxml import etree
import re
import json
import subprocess
from pathlib import Path

import duckdb

DEFAULT_WHITELIST = [
    "tlg0543", # Polybius
    "tlg0527", # Septuagint
    "tlg0007", # Plutarch
    "tlg0557", # Epictetus
    "tlg0062", # Lucian
    "tlg0525", # Pausanius
    "tlg0057", # Galen
    "tlg0551", # Appian
    "tlg0526", # Josephus
]

GREEK_PUNCTUATION = re.compile(r'([.;·?])\s+')

DEFAULT_ADDITIONAL_TEXT_PATH = 'data/combined_text_NT.txt'


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _split_into_sentences(text: str):
    sentences = []
    chunks = GREEK_PUNCTUATION.split(text)
    for i in range(0, len(chunks) - 1, 2):
        sent = (chunks[i] + chunks[i + 1]).strip()
        if len(sent) > 5:
            sentences.append(sent)
    return sentences


def build_greek_corpus_from_dbt(
    whitelist: list=None,
    run_dbt: bool=True,
    dbt_project_dir: str="dbt",
    db_path: str="data/greek_training.duckdb",
    additional_text_path: str=None,
):
    """
    Returns sentence-level Greek text from the dbt model `analytics.stg_corpus`
    plus supplemental text not yet present in dbt.

    If `run_dbt=True`, this function first executes dbt with an override for
    `author_whitelist`, then reads `verse_text` rows from DuckDB.
    """
    if whitelist is None:
        whitelist = DEFAULT_WHITELIST

    if additional_text_path is None:
        additional_text_path = DEFAULT_ADDITIONAL_TEXT_PATH

    root = _repo_root()
    dbt_dir = root / dbt_project_dir
    warehouse_path = root / db_path

    if run_dbt:
        env = os.environ.copy()
        env["DBT_PROFILES_DIR"] = str(dbt_dir)
        subprocess.run(
            [
                "uv",
                "run",
                "dbt",
                "run",
                "--select",
                "stg_corpus",
            ],
            cwd=str(dbt_dir),
            env=env,
            check=True,
        )

    if not warehouse_path.exists():
        raise FileNotFoundError(f"DuckDB file not found at {warehouse_path}")

    with duckdb.connect(str(warehouse_path), read_only=True) as con:
        if whitelist:
            placeholders = ", ".join(["?"] * len(whitelist))
            query = f"""
            select verse_text
            from analytics.stg_corpus
            where
                verse_text is not null and
                trim(verse_text) <> '' and
                author_id in ({placeholders})
            order by verse_id
            """
            rows = con.execute(query, whitelist).fetchall()
        else:
            rows = con.execute(
                """
                select verse_text
                from analytics.stg_corpus
                where
                    verse_text is not null and
                    trim(verse_text) <> ''
                order by verse_id
                """
            ).fetchall()

    corpus = [row[0] for row in rows]

    additional_path = Path(additional_text_path)
    if not additional_path.is_absolute():
        additional_path = root / additional_path

    if additional_path.exists():
        supplemental_text = additional_path.read_text(encoding="utf-8")
        corpus.extend(_split_into_sentences(supplemental_text))
        print(f"Added additional text from {additional_path}")

    return corpus

def build_greek_corpus(repo_path: str = "~/Documents/codespace/projects/First1KGreek", additional_text_path: str=None, whitelist: list=None):
    """
    Parses First1KGreek XML files based on a whitelist, merges with 
    additional text, and returns a list of cleaned sentences.

    Default whitelist includes Polybius, Septuagint, Plutarch, Epictetus, Lucian, Pausanius, Galen, Appian, Josephus
    """
    if whitelist is None:
        whitelist = DEFAULT_WHITELIST

    if additional_text_path is None:
        additional_text_path = DEFAULT_ADDITIONAL_TEXT_PATH

    repo_path = os.path.expanduser(repo_path)
    all_text = []
    
    # 1. Extract from XML files
    search_pattern = os.path.join(repo_path, "data", "**", "*.xml")
    files = glob.glob(search_pattern, recursive=True)
    
    print(f"Found {len(files)} total XML files. Filtering by whitelist...")

    for xml_file in files:
        parts = xml_file.split(os.sep)
        if 'data' in parts:
            data_index = parts.index('data')
            author_id = parts[data_index + 1]
            
            if author_id in whitelist:
                try:
                    tree = etree.parse(xml_file)
                    root = tree.getroot()
                    text_content = " ".join(root.xpath("//*[local-name()='body']//text()"))
                    clean_str = " ".join(text_content.split())
                    if clean_str:
                        all_text.append(clean_str)
                except Exception as e:
                    print(f"Error parsing {xml_file}: {e}")

    # 2. Add supplementary text (e.g., NT Greek)
    if additional_text_path and os.path.exists(additional_text_path):
        with open(additional_text_path, 'r', encoding='utf-8') as f:
            all_text.append(f.read())
        print(f"Added additional text from {additional_text_path}")

    # 3. Process into sentences
    sentences = []
    for text in all_text:
        sentences.extend(_split_into_sentences(text))

    return sentences

if __name__ == "__main__":

    path = "~/Documents/codespace/projects/First1KGreek"
    extra = "data/combined_text.txt"
    
    results = build_greek_corpus(path, extra)
    print(f"Total sentences extracted: {len(results)}")
    
    with open('data/greek_corpus.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(results))