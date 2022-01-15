import re
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import List, Tuple


class QuestionGenerator:

    def __init__(self) -> None:

        checkpoint = "Sabokou/squad-qg-gen"
        self.answer_token = "<ANWSR>"
        self.context_token = "<CNTXT>"
        self.sequence_length = 1024

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")

        self.qg_tokenizer = AutoTokenizer.from_pretrained(checkpoint, use_fast=False)
        self.qg_model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
        self.qg_model.to(self.device)
        self.qg_model.eval()

    def generate(self, text: str) -> List:

        qg_inputs, qg_answers = self.generate_qg_inputs(text)
        generated_questions = self.generate_questions_from_inputs(qg_inputs)

        qa_list = self._get_all_qa_pairs(generated_questions, qg_answers)

        return qa_list

    def generate_qg_inputs(self, text: str) -> Tuple[List[str], List[str]]:

        inputs = list()
        answers = list()

        segments = self._split_into_segments(text)

        for segment in segments:
            sentences = self._split_text(segment)
            prepped_inputs, prepped_answers = self._prepare_qg_inputs(sentences, segment)
            inputs.extend(prepped_inputs)
            answers.extend(prepped_answers)

        return inputs, answers

    def generate_questions_from_inputs(self, qg_inputs: List) -> List[str]:

        generated_questions = list()

        for qg_input in qg_inputs:
            question = self._generate_question(qg_input)
            generated_questions.append(question)

        return generated_questions

    @staticmethod
    def _split_text(text: str) -> List[str]:
        """Splits the text into sentences and shortens longer sentences."""
        max_sentence_length = 128
        sentences = re.findall(r".*?[.!\?]", text)
        cut_sentences = []

        for sentence in sentences:
            if len(sentence) > max_sentence_length:
                cut_sentences.extend(re.split("[,;:)]", sentence))

        # remove useless post-quote sentence fragments
        cut_sentences = [s for s in sentences if len(s.split(" ")) > 5]
        sentences = sentences + cut_sentences

        return list(set([s.strip(" ") for s in sentences]))

    def _split_into_segments(self, text: str) -> List[str]:
        """Splits a long text into segments short enough to be input into the transformer network.
        Segments are used as context for question generation.
        """
        max_tokens = 490
        paragraphs = text.split("\n")
        tokenized_paragraphs = [
            self.qg_tokenizer(p)["input_ids"] for p in paragraphs if len(p) > 0
        ]
        segments = []

        while len(tokenized_paragraphs) > 0:
            segment = []

            while len(segment) < max_tokens and len(tokenized_paragraphs) > 0:
                paragraph = tokenized_paragraphs.pop(0)
                segment.extend(paragraph)
            segments.append(segment)

        return [self.qg_tokenizer.decode(s, skip_special_tokens=True) for s in segments]

    def _prepare_qg_inputs(self, sentences: List[str], text: str) -> Tuple[List[str], List[str]]:

        inputs = list()
        answers = list()

        for sentence in sentences:
            qg_input = f"{self.answer_token} {sentence} {self.context_token} {text}"
            inputs.append(qg_input)
            answers.append(sentence)

        return inputs, answers

    @torch.no_grad()
    def _generate_question(self, qg_input: str) -> str:
        encoded_input = self._encode_qg_input(qg_input)
        output = self.qg_model.generate(input_ids=encoded_input["input_ids"])
        question = self.qg_tokenizer.decode(
            output[0],
            skip_special_tokens=True
        )
        return question

    def _encode_qg_input(self, qg_input: str) -> torch.tensor:
        return self.qg_tokenizer(
            qg_input,
            padding='max_length',
            max_length=self.sequence_length,
            truncation=True,
            return_tensors="pt",
        ).to(self.device)

    @staticmethod
    def _get_all_qa_pairs(generated_questions: List[str], qg_answers: List[str]):
        """Formats question and answer pairs without ranking or filtering."""
        qa_list = []

        for question, answer in zip(generated_questions, qg_answers):
            qa = {
                "question": question.split("?")[0] + "?",
                "answer": answer
            }
            qa_list.append(qa)
        return qa_list