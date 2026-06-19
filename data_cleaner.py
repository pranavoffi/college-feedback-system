import pandas as pd
import requests
import json

STANDARD_FIELDS = ["ID", "Department", "Teacher", "FeedbackText"]


def smart_map_columns(csv_path):
    """Load CSV, map columns using LLM with spell correction, return clean DataFrame"""
    df = pd.read_csv(csv_path)
    print(f"📁 Loaded CSV with columns: {list(df.columns)}")

    # Try LLM mapping first
    mapping = get_llm_mapping(df.columns) or create_fallback_mapping(df.columns)

    # Apply mapping and clean
    mapped_df = pd.DataFrame()
    for orig_col, std_field in mapping.items():
        if orig_col in df.columns and std_field in STANDARD_FIELDS:
            mapped_df[std_field] = df[orig_col].astype(str).str.strip()

    # Remove rows with missing values
    clean_df = mapped_df.dropna().reset_index(drop=True)

    print(f"✅ Mapped {len(mapping)} columns, extracted {len(clean_df)} clean rows")
    print("\nColumn Mapping:")
    for orig, std in mapping.items():
        print(f"  {orig} → {std}")

    return clean_df


def get_llm_mapping(columns):
    """Try to get mapping from LLM"""
    prompt = f"""Map CSV columns to: ID, Department, Teacher, FeedbackText
Columns: {list(columns)}
Return only JSON like: {{"id": "ID", "dept": "Department", "professor": "Teacher", "tudentcomments": "FeedbackText"}}"""

    try:
        response = requests.post("http://localhost:11434/api/generate",
                                 json={"model": "llama3.2:3b", "prompt": prompt, "stream": False,
                                       "options": {"temperature": 0, "num_predict": 150}}, timeout=20)

        output = response.json()["response"].strip()
        print(f"🤖 LLM response: {output}")

        # Multiple JSON extraction attempts
        for attempt in [
            lambda x: json.loads(x[x.find("{"):x.rfind("}") + 1]),
            lambda x: json.loads(x.split('\n')[0] if x.startswith('{') else x[x.find('{'):]),
            lambda x: json.loads(x.replace("'", '"'))
        ]:
            try:
                return attempt(output)
            except:
                continue

    except Exception as e:
        print(f"⚠️ LLM failed: {e}")
    return None


def create_fallback_mapping(columns):
    """Create mapping using fuzzy matching as fallback"""
    mapping = {}

    # Smart mapping rules
    rules = {
        'ID': ['id', 'identifier', 'number', 'num'],
        'Department': ['dept', 'department', 'dep', 'division', 'dept_name'],
        'Teacher': ['teacher', 'professor', 'prof', 'instructor', 'faculty'],
        'FeedbackText': ['feedback', 'comment', 'text', 'tudentcomment', 'studentcomment', 'review']
    }

    for col in columns:
        col_lower = col.lower()
        for std_field, keywords in rules.items():
            if any(keyword in col_lower for keyword in keywords):
                mapping[col] = std_field
                break

    print("🔧 Using fallback mapping")
    return mapping




if __name__ == "__main__":

    file_path = input("Enter your CSV file path: ").strip()
    if file_path:
        result_df = smart_map_columns(file_path)
        print(f"\n📊 Final DataFrame:\n{result_df}")















