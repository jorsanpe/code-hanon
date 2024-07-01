supported = {
    "ruby": {
        "extensions": ["*.rb"],
        "reserved_words": ["class", "module", "do", "map", "expect", "to", "eq", "def", "end", "if", "it", "require",
                           "nil"]
    },
    "python": {
        "extensions": ["*.py"],
        "reserved_words": ["class", "return", "import", "from", "def", "if", "for", "while", "with", "in", "and", "not",
                           "or", "self"]
    },
    "c": {
        "extensions": ["*.c", "*.h"],
        "reserved_words": ["for", "while", "do", "const", "statis", "void", "#include", "#ifndef", "#define", "#endif"],
        "comments": r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"'
    }
}
