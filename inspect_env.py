try:
    with open('.env', 'rb') as f:
        content = f.read()
    print(f"Raw content repr: {content!r}")
except Exception as e:
    print(f"Error reading .env: {e}")
