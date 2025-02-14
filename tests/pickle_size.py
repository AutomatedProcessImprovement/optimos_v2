import pickle
import sys


def build_size_tree(obj, seen=None):
    """
    Recursively builds a complete tree with size information of an object.

    Each node in the tree is a dictionary with:
      - 'type': the object's type name.
      - 'shallow_size': the size of the object itself (via sys.getsizeof).
      - 'total_size': the shallow size plus sizes of children (if any).
      - 'children': a dict mapping attribute/key/index to child node info (if any).
      - 'note': optional note (e.g., if an object is already seen).

    This function descends into all levels of the object structure.
    """
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        # Object already processed; avoid double counting.
        return {
            "type": type(obj).__name__,
            "shallow_size": 0,
            "total_size": 0,
            "note": "Already counted",
        }
    seen.add(obj_id)

    shallow = sys.getsizeof(obj)
    total = shallow
    info = {"type": type(obj).__name__, "shallow_size": shallow, "total_size": shallow}

    children = {}
    # For dictionaries, process the values.
    if isinstance(obj, dict):
        for key, value in obj.items():
            subtree = build_size_tree(value, seen)
            children[f"dict key: {key}"] = subtree
            total += subtree["total_size"]
    # For iterables (but not strings/bytes), process each item.
    elif isinstance(obj, (list, tuple, set, frozenset)):
        for index, item in enumerate(obj):
            subtree = build_size_tree(item, seen)
            children[f"index: {index}"] = subtree
            total += subtree["total_size"]
    # For objects with a __dict__, process its attributes.
    elif hasattr(obj, "__dict__"):
        for key, value in vars(obj).items():
            subtree = build_size_tree(value, seen)
            children[f"attr: {key}"] = subtree
            total += subtree["total_size"]

    if children:
        info["children"] = children
        info["total_size"] = total

    return info


def print_size_tree(tree, current_depth=0, max_print_depth=5):
    """
    Pretty-prints the size tree up to max_print_depth levels deep.

    If there are deeper levels beyond max_print_depth, it prints '...'
    to indicate additional depth.
    """
    indent = " " * (current_depth * 4)
    line = f"{indent}{tree.get('type')}: shallow = {tree.get('shallow_size')} bytes, total = {tree.get('total_size')} bytes"
    if "note" in tree:
        line += f" ({tree['note']})"
    print(line)

    if "children" in tree:
        # Only print children if we haven't hit our max print depth.
        if current_depth < max_print_depth - 1:
            for key, subtree in tree["children"].items():
                print(f"{indent}  -> {key}:")
                print_size_tree(subtree, current_depth + 1, max_print_depth)
        else:
            # At max depth; just indicate that there are more details.
            print(f"{indent}  -> ... (deeper levels not shown)")


# --- Example Usage ---
# Load your pickle file:
with open(sys.argv[1], "rb") as f:
    data = pickle.load(f)

# Build the complete size tree (all levels are computed)
size_tree = build_size_tree(data)

# Print the size tree, but only show up to 5 levels deep.
print("Size breakdown (printed up to 5 levels deep):")
print_size_tree(size_tree, max_print_depth=5)
