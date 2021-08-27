import os 


languages={
 }

def fill_out_dicionary():
    global languages
    languages_files = os.listdir('languages')

    for lang in languages_files:
        if lang[len(lang)-2:]=='py':
                lang_model_name = lang.split('.')[0]
                language_file = __import__(f'languages.{lang_model_name}', fromlist=['object'])
                languages[language_file.language_shortcut]=language_file.translation



			



