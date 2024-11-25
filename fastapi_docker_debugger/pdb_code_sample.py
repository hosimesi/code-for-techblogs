import pdb


def main() -> int:
    a = 1
    b = 2
    pdb.set_trace() # breakpoint()でも可
    c = a + b
    return c


if __name__ == "__main__":
    result = main()
