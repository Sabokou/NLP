import docx2txt

# read in word file
result = docx2txt.process("Zusammenfassung.docx")

print(result)

import mammoth

with open("Zusammenfassung.docx", "rb") as docx_file:
    result = mammoth.convert_to_html(docx_file)
    text = result.value
  #  with open('output.html', 'w') as html_file:
   #     html_file.write(text)

#print(text)