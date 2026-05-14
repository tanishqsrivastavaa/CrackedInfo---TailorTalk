from app.services.google_drive import search_by_name, search_files, search_pdfs, search_folders

files = search_folders("pics")

for file in files:
    print(file)
