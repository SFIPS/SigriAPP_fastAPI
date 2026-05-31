"""
Serialization strategy for Android-compatible JSON output.

THE PROBLEM:
  Pydantic's model_dump() produces keys in alphabetical order:
    {"BARRIO": ..., "DEPARTAMENTO": ..., "DIRECCION": ...}
  Android's JsonReader expects:
    {"ID_PROGRAMACION": ..., "ESTADO": ..., "DIRECCION": ..., ...}

  model_dump(mode="json") converts None to null, which causes:
    nextString() skip → field not set → stale data in POJO

THE SOLUTION:
  NEVER use model_dump() on response data.
  Use OrderedDict factories in models/programacion.py instead.

GOLDEN RULES:
  1. Build all responses as OrderedDict with exact key order
  2. Set null NEVER — use "" for empty strings
  3. JSONResponse(content=ordered_dict) preserves insertion order
  4. LATITUD/LONGITUD must be strings — use str(value), not float
  5. Include ALL 16 keys even if empty
  6. MOTVISITA2 must be present in Default branch
  7. VISITA may be absent in historia_nueva branch
"""
