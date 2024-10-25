"""Console script for near_dedup."""

import fire


def help() -> None:
    print("near_dedup")
    print("=" * len("near_dedup"))
    print("few basic experiments for the Bloom filter and use LSH for the near")

def main() -> None:
    fire.Fire({
        "help": help
    })


if __name__ == "__main__":
    main() # pragma: no cover
