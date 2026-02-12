try:
    from .main import main
except ImportError:
    from app.main import main

if __name__ == "__main__":
    main()
