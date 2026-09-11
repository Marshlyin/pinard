import uvicorn


def main() -> None:
    uvicorn.run(
        "src.app:create_app",
        host="127.0.0.1",
        port=9090,
        log_config=None,
        reload=True,
        factory=True,
    )


if __name__ == "__main__":
    main()
