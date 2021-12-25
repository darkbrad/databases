import hashlib
import base64

10001111_00011010_0101010_10101010_01010


def main() -> None:
    text = "12345"

    print(text)
    print(text.encode("utf-8"))
    hashed = hashlib.sha256(text.encode("utf-8")).digest()

    print(base64.b16encode(hashed))
    print(base64.b32encode(hashed))
    print(base64.b64encode(hashed))
    print(base64.b85encode(hashed))


if __name__ == "__main__":
    main()
