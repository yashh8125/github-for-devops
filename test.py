import hashlib


def generate_md5_hash(text: str) -> str:
    """Return the MD5 hash of the given text."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    try:
        value = input("Enter text to hash: ")
        print("MD5:", generate_md5_hash(value))
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
