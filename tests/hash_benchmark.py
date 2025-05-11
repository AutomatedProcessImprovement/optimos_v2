# Use deep_hash
import pickle
import time


from o2.util.helper import hash_int

with open(
    "stores/run_2025-03-04-23-10-00-422042/states/state_simulated_annealing_production_mid_1342702810.pkl",
    "rb",
) as f:
    state = pickle.load(f)


# def deep_hash(obj: Any) -> int:
#     """Recursively compute a hash for nested frozen dataclasses and other basic types."""
#     if isinstance(obj, (str, bytes, bytearray, memoryview)):
#         return xxhash.xxh3_64_intdigest(obj)
#     if isinstance(obj, (int, bool)):
#         return xxhash.xxh3_64_intdigest(bytes(obj))
#     if isinstance(obj, (float, type(None))):
#         return xxhash.xxh3_64_intdigest(str(obj))
#     elif isinstance(obj, (list, tuple)):
#         # Hash sequences by hashing the bytearray of item hashes
#         return xxhash.xxh3_64_intdigest(
#             bytearray(b for item in obj for b in deep_hash(item).to_bytes(8, "big"))
#         )
#     elif isinstance(obj, dict):
#         # Hash dict by hashing sorted (key, value) pairs
#         return xxhash.xxh3_64_intdigest(
#             bytearray(
#                 h for k, v in sorted(obj.items()) for h in (deep_hash(k), deep_hash(v))
#             )
#         )
#     elif is_dataclass(obj):
#         # Hash dataclass by hashing a tuple of its field hashes
#         return xxhash.xxh3_64_intdigest(
#             bytearray(
#                 b
#                 for f in fields(obj)
#                 for b in deep_hash(getattr(obj, f.name)).to_bytes(8, "big")
#             )
#         )

#     elif isinstance(obj, TimePeriod):
#         return obj.id

#     # support pydantic
#     elif isinstance(obj, BaseModel):
#         return xxhash.xxh3_64_intdigest(obj.model_dump_json())
#     else:
#         raise TypeError(f"Unsupported type: {type(obj)}")


# def deep_hash(obj: Any) -> int:
#     hash_instance = xxhash.xxh3_64()

#     def deep_hash_inner(obj: Any):
#         """Recursively compute a hash for nested frozen dataclasses and other basic types."""
#         if isinstance(obj, (str, bytes, bytearray, memoryview)):
#             hash_instance.update(obj)
#         elif isinstance(obj, (int, bool)):
#             hash_instance.update(bytes(obj))
#         elif isinstance(obj, (float, type(None))):
#             hash_instance.update(str(obj))
#         elif isinstance(obj, (list, tuple)):
#             # Hash sequences by hashing the bytearray of item hashes
#             hash_instance.update(
#                 bytearray(b for item in obj for b in deep_hash(item).to_bytes(8, "big"))
#             )
#         elif isinstance(obj, dict):
#             # Hash dict by hashing sorted (key, value) pairs
#             hash_instance.update(
#                 bytearray(
#                     h
#                     for k, v in sorted(obj.items())
#                     for h in (deep_hash(k), deep_hash(v))
#                 )
#             )
#         elif is_dataclass(obj):
#             # Hash dataclass by hashing a tuple of its field hashes
#             hash_instance.update(
#                 bytearray(
#                     b
#                     for f in fields(obj)
#                     for b in deep_hash(getattr(obj, f.name)).to_bytes(8, "big")
#                 )
#             )

#         elif isinstance(obj, TimePeriod):
#             return obj.id

#         # support pydantic
#         elif isinstance(obj, BaseModel):
#             hash_instance.update(obj.model_dump_json())
#         else:
#             raise TypeError(f"Unsupported type: {type(obj)}")

#         return

#     deep_hash_inner(obj)
#     return hash_instance.intdigest()


# from dataclasses import fields, is_dataclass
# from typing import Any
# from dataclasses import fields, is_dataclass
# from typing import Any

# from pydantic import BaseModel

# from o2.models.timetable.time_period import TimePeriod
# from o2.util.helper import hash_int


# def deep_hash(obj: Any) -> int:
#     """Recursively compute a hash for nested frozen dataclasses and other basic types."""
#     if isinstance(obj, (str, int, float, bool, bytes, type(None))):
#         return hash_int(obj)

#     elif isinstance(obj, (list, tuple)):
#         # Hash sequences by hashing the tuple of item hashes
#         return hash_int(tuple(deep_hash(item) for item in obj))

#     elif isinstance(obj, dict):
#         # Hash dict by hashing sorted (key, value) pairs
#         return hash_int(
#             tuple(sorted((deep_hash(k), deep_hash(v)) for k, v in obj.items()))
#         )

#     elif is_dataclass(obj):
#         # Hash dataclass by hashing a tuple of its field hashes
#         return hash_int(tuple(deep_hash(getattr(obj, f.name)) for f in fields(obj)))

#     elif isinstance(obj, TimePeriod):
#         return obj.id

#     # support pydantic
#     elif isinstance(obj, BaseModel):
#         return hash_int(obj.model_dump_json())
#     else:
#         raise TypeError(f"Unsupported type: {type(obj)}")


start_time = time.time()
for _ in range(1000):
    hash_int(state.timetable.to_json())
end_time = time.time()

avg_time = (end_time - start_time) / 100
total_time = end_time - start_time
print(f"Time taken: {avg_time:3f} (avg) {total_time:3f} (total) seconds")
