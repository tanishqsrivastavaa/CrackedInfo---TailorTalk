from app.services.google_drive import search_by_name, search_files

files = search_by_name("")

for file in files:
    print(file)
