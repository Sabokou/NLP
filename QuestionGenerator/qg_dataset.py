import pandas as pd
import random
import datasets
import torch
from transformers import AutoTokenizer


class CustomQGDataset(torch.utils.data.Dataset):
    def __int__(self,
                tokenizer: AutoTokenizer,
                data: datasets.Dataset,
                max_length: int,
                pad_mask_id: int):
        self.data = pd.Dataframe(data)
        self.max_length = max_length
        self.pad_mask_id = pad_mask_id
        self.tokenizer = tokenizer

    def __getitem__(self, item_index: int):
        item = self.data.iloc[item_index]
        input_ids, attention_mask = self._tokenize_text(item.kontext)
        labels, _ = self._tokenize_text(item.frage)
        masked_labels = self._mask_label_padding(labels)
        return {"input_ids": input_ids,
                "attention_mask": attention_mask,
                "labels": labels}

    def _tokenize_text(self, text: str):
        tokenized_text = self.tokenizer(
            text,
            padding="max_length",
            max_length=self.max_length,
            truncation=True,
            return_tensors="pt"
        )
        return (tokenized_text["input_ids"].squeeze(),
                tokenized_text["attention_mask"].squeeze())

    def _mask_label_padding(self, labels: torch.Tensor) -> torch.Tensor:
        labels[labels == self.tokenizer.pad_token_id] = self.pad_mask_id
        return labels
