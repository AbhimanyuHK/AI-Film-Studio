import uvicorn


def main() -> None:
    uvicorn.run('film_runtime.api:app', host='0.0.0.0', port=8081, reload=False)


if __name__ == '__main__':
    main()
