from app.qg import QuestionGenerator

qg=QuestionGenerator()

text = "Computational linguistics is an interdisciplinary field concerned with the computational modelling of natural language, as well as the study of appropriate computational approaches to linguistic questions. In general, computational linguistics draws upon linguistics, computer science, artificial intelligence, mathematics, logic, philosophy, cognitive science, cognitive psychology, psycholinguistics, anthropology and neuroscience, among others."

question_answer_dict = qg.generate(text)

question_answer_list = []

for i in range(len(question_answer_dict)):
    inner_list = []
    for j in question_answer_dict[i].keys():
        inner_list.append(question_answer_dict[i][j])
    question_answer_list.append(inner_list)

print(question_answer_list)