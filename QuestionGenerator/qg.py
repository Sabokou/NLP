import re
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import List, Tuple, Dict


class QuestionGenerator:
    """This class is provided as an all-in-one solution to fetch the model, prepare given text to be used in the model
    and to generate questions."""
    def __init__(self) -> None:
        checkpoint = "Sabokou/squad-qg-gen"
        self.answer_token = "<ANWSR>"
        self.context_token = "<CNTXT>"
        self.sequence_length = 512

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        # Fetch models online from Huggingface --> could theoratically be modified to use local directory instead
        self.qg_tokenizer = AutoTokenizer.from_pretrained(checkpoint, use_fast=False)
        self.qg_model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
        # Cast model to selected device
        self.qg_model.to(self.device)
        # Set model to eval mode to prevent gradient calculations
        self.qg_model.eval()
        print("Class created")

    def generate(self, text: str) -> List[Dict]:
        """
        All-in-one function to delegate the creation of questions given the passed string.
        :param text: string containing the large context from which questions shall be created
        :return:
        List - 1-n dictionaries containing Question and Answer pairs
        """
        # get list of inputs and answers
        qg_inputs, qg_answers = self.generate_qg_inputs(text)
        # create questions based on input string (answer + context)
        generated_questions = self.generate_questions_from_inputs(qg_inputs)
        # Logging function during testing
        # print("Generated questions: {generated_questions}")

        # create pairs from answers and generated questions
        qa_list = self._get_all_qa_pairs(generated_questions, qg_answers)
        # remove duplicate questions (might discard "better" question answer pairs)
        qa_list = self._remove_duplicate_questions(qa_list)
        return qa_list

    def generate_qg_inputs(self, text: str) -> Tuple[List[str], List[str]]:
        """
        Prepare inputs for the model by segmenting the text.
        :param text:
        :return:
        """
        inputs = list()
        answers = list()
        # create segments
        segments = self._split_into_segments(text)
        # create answers and context from each segment
        for segment in segments:
            # create sentences from a segment
            sentences = self._split_text(segment)
            # get inputs and answer segments
            prepped_inputs, prepped_answers = self._prepare_qg_inputs(sentences, segment)
            inputs.extend(prepped_inputs)
            answers.extend(prepped_answers)

        return inputs, answers

    def generate_questions_from_inputs(self, qg_inputs: List) -> List[str]:
        """
        Generates questions given a list of tokenized strings.
        :param qg_inputs:
        :return:
        """
        generated_questions = list()
        # Generate a question for each input
        for qg_input in qg_inputs:
            question = self._generate_question(qg_input)
            generated_questions.append(question)

        return generated_questions

    @staticmethod
    def _split_text(text: str) -> List[str]:
        """
        Splits the text into sentences and shortens longer sentences.
        :param text:
        :return:
        """
        max_sentence_length = 128
        sentences = re.findall(r".*?[.!\?]", text)
        cut_sentences = []

        for sentence in sentences:
            # If given text is longer then the max length it is cut at every
            if len(sentence) > max_sentence_length:
                cut_sentences.extend(re.split("[,;:)]", sentence))

        # remove useless post-quote sentence fragments
        cut_sentences = [s for s in sentences if len(s.split(" ")) > 5]
        sentences = sentences + cut_sentences

        return list(set([s.strip(" ") for s in sentences]))

    def _split_into_segments(self, text: str) -> List[str]:
        """
        Splits a long text into segments short enough to be input into the transformer model.
        Segments are used as context for question generation.
        :param text:
        :return:
        """
        max_tokens = 490
        paragraphs = text.split("\n")
        # call tokenizer for each paragraph
        tokenized_paragraphs = [
            self.qg_tokenizer(p)["input_ids"] for p in paragraphs if len(p) > 0
        ]
        segments = []

        # if there are still paragraphs
        while len(tokenized_paragraphs) > 0:
            segment = []
            # if the segment is of usable length it will be added
            while len(segment) < max_tokens and len(tokenized_paragraphs) > 0:
                paragraph = tokenized_paragraphs.pop(0)
                segment.extend(paragraph)
            segments.append(segment)

        return [self.qg_tokenizer.decode(s, skip_special_tokens=True) for s in segments]

    def _prepare_qg_inputs(self, sentences: List[str], text: str) -> Tuple[List[str], List[str]]:
        """
        Concatenates the list of answers and the context with tokens.
        :param sentences: List of Answer strings
        :param text: List of contexts
        :return: List
        """
        inputs = list()
        answers = list()

        for sentence in sentences:
            # Concat the "answer string" and the "context" with tokens
            qg_input = f"{self.answer_token} {sentence} {self.context_token} {text}"
            inputs.append(qg_input)
            answers.append(sentence)

        return inputs, answers

    @torch.no_grad()
    def _generate_question(self, qg_input: str) -> str:
        """
        Encodes input string and generate and returns a
        :param qg_input:
        :return:
        """
        # Create inputs for model
        encoded_input = self._encode_qg_input(qg_input)
        # Feed input into model
        output = self.qg_model.generate(input_ids=encoded_input["input_ids"])
        # decode model output to be human-readable again
        question = self.qg_tokenizer.decode(
            output[0],
            skip_special_tokens=True
        )
        return question

    def _encode_qg_input(self, qg_input: str) -> torch.tensor:
        """
        Returns tokenized version of input string
        :param qg_input: string representing the answer and context
        :return:
            Tensor
        """
        return self.qg_tokenizer(
            qg_input,
            padding='max_length',
            max_length=self.sequence_length,
            truncation=True,
            return_tensors="pt",
        ).to(self.device)

    @staticmethod
    def _get_all_qa_pairs(generated_questions: List[str], qg_answers: List[str]):
        """
        Formats question and answer pairs without ranking or filtering.
        :param generated_questions:
        :param qg_answers:
        :return:
        """
        qa_list = []
        # create iterator for both lists to be iterated over simultaneously
        for question, answer in zip(generated_questions, qg_answers):
            # combine question and answer
            qa = {
                "question": question.split("?")[0] + "?",
                "answer": answer
            }
            qa_list.append(qa)
        return qa_list

    @staticmethod
    def _remove_duplicate_questions(question_list: List[Dict]) -> List[Dict]:
        """
        Generator sometimes produces duplicate questions that lead to problems in the database.
        :param question_list:
        :return:
        List
            List of Question-Answer Dictionaries without duplicates
        """
        questions = list()
        return_list = list()
        # Iterates through all question-answer dictionaries
        for question_pair in question_list:
            # Fetch current question
            question = question_pair.get("question")
            # Checks if question string was previously created
            if question not in questions:
                # If question is new appends to question list
                questions.append(question)
                return_list.append(question_pair)

        return return_list


if __name__ == "__main__":
    qg = QuestionGenerator()
    output = qg.generate("""Computational linguistics is often grouped within the field of artificial intelligence but was present before the development of artificial intelligence. Computational linguistics originated with efforts in the United States in the 1950s to use computers to automatically translate texts from foreign languages, particularly Russian scientific journals, into English. Since computers can make arithmetic (systematic) calculations much faster and more accurately than humans, it was thought to be only a short matter of time before they could also begin to process language. Computational and quantitative methods are also used historically in the attempted reconstruction of earlier forms of modern languages and sub-grouping modern languages into language families. Earlier methods, such as lexicostatistics and glottochronology, have been proven to be premature and inaccurate. However, recent interdisciplinary studies that borrow concepts from biological studies, especially gene mapping, have proved to produce more sophisticated analytical tools and more reliable results.
When machine translation (also known as mechanical translation) failed to yield accurate translations right away, automated processing of human languages was recognized as far more complex than had originally been assumed. Computational linguistics was born as the name of the new field of study devoted to developing algorithms and software for intelligently processing language data. The term "computational linguistics" itself was first coined by David Hays, a founding member of both the Association for Computational Linguistics (ACL) and the International Committee on Computational Linguistics (ICCL).
To translate one language into another, it was observed that one had to understand the grammar of both languages, including both morphology (the grammar of word forms) and syntax (the grammar of sentence structure). To understand syntax, one had to also understand the semantics and the lexicon (or 'vocabulary'), and even something of the pragmatics of language use. Thus, what started as an effort to translate between languages evolved into an entire discipline devoted to understanding how to represent and process natural languages using computers.
Nowadays research within the scope of computational linguistics is done at computational linguistics departments, computational linguistics laboratories, computer science departments, and linguistics departments. Some research in the field of computational linguistics aims to create working speech or text processing systems while others aim to create a system allowing human-machine interaction. Programs meant for human-machine communication are called conversational agents.
""")
    print(output)
