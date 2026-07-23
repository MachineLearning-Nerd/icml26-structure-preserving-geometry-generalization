def pytest_addoption(parser):
    parser.addoption(
        "--geo-new-source-tar",
        action="store",
        default=None,
        help="Path to the SHA-pinned arXiv 2602.02788v2 source archive.",
    )

