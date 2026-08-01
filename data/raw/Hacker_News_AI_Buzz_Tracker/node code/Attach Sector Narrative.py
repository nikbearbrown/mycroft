# n8n code node: Attach Sector Narrative  (Week 9 — parse the sector Groq response)
# Wire to: Save Snapshot, Code in Python, If  (the True-branch terminal node).
import json
import re

def extract_json_object(text):
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    if text.startswith("{"):
        return text
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in model output")
    return text[start:end + 1]

def build(_items):
    row = _items[0]["json"]["row"]
    try:
        j = _items[0]["json"]
        if "choices" not in j:
            raise RuntimeError(f"Groq error: {j.get('error') or j}")
        content = j["choices"][0]["message"]["content"]
        o = json.loads(extract_json_object(content))
        row["sectorNarrative"] = {"narrative": (o.get("sectorNarrative") or "").strip(),
                                    "crossEntityThemes": (o.get("crossEntityThemes") or [])[:6],
                                    "degraded": False}
    except Exception as ex:
        row["sectorNarrative"] = {"narrative": None, "crossEntityThemes": [],
                                    "degraded": True, "reason": str(ex)}
    return [{"json": row}]


return build(_items)
