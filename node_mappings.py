try:
    from .nodes.tokens import *
except ImportError:
    print("\033[34mftechmax Custom Nodes: \033[92mFailed to load nodes\033[0m")
    pass

NODE_CLASS_MAPPINGS = {
    "CountTokens": CountTokens,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CountTokens": "Count Tokens",
}