def insert_text_to_file(filepath, text_to_insert):
    try:
        with open(filepath, 'w') as file:
            file.write(text_to_insert)
        print(f"Text successfully written to {filepath}")
    except Exception as e:
        print(f"An error occurred: {e}")

