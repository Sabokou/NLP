from app.QuestionGenerator.qg import QuestionGenerator

qg=QuestionGenerator()

text = "Computational linguistics is an interdisciplinary field concerned with the computational modelling of natural language, as well as the study of appropriate computational approaches to linguistic questions. In general, computational linguistics draws upon linguistics, computer science, artificial intelligence, mathematics, logic, philosophy, cognitive science, cognitive psychology, psycholinguistics, anthropology and neuroscience, among others."

question_answer_list = qg.generate(text)
print(question_answer_list)