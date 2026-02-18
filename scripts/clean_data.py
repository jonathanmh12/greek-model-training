import os
import glob
from lxml import etree
import re

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

def build_greek_corpus(repo_path: str = "~/Documents/codespace/projects/First1KGreek", additional_text_path=None, whitelist=None):
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
        chunks = GREEK_PUNCTUATION.split(text)
        # Re-join punctuation with the preceding chunk
        for i in range(0, len(chunks)-1, 2):
            sent = (chunks[i] + chunks[i+1]).strip()
            if len(sent) > 5:
                sentences.append(sent)
                
    return sentences

if __name__ == "__main__":

    path = "~/Documents/codespace/projects/First1KGreek"
    extra = "data/combined_text.txt"
    
    results = build_greek_corpus(path, extra)
    print(f"Total sentences extracted: {len(results)}")
    
    with open('data/greek_corpus.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(results))