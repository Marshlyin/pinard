import uvicorn


def main() -> None:
    uvicorn.run(
        "src.app:create_production_app",
        host="0.0.0.0",  # noqa: S104 (écoute sur toutes les interfaces : nécessaire dans le conteneur)
        port=8000,
        log_config=None,
        factory=True,
        # Un seul worker : SQLite n'accepte qu'un écrivain à la fois
        workers=1,
    )


if __name__ == "__main__":
    main()
