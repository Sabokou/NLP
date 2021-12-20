import docx2txt

# read in word file
#result = docx2txt.process("Zusammenfassung.docx")

#print(result)

import mammoth

with open("Wikipedia-Article-NLP.docx", "rb") as docx_file:
    result = mammoth.convert_to_html(docx_file, ignore_empty_paragraphs=False)
    text = result.value
    messages=result.messages
    with open('output.html', 'w') as html_file:
       html_file.write(text)

print(text)
print(messages)