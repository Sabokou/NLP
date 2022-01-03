# Torch imports
import datasets
import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset

# Evaluation method
from sklearn.metrics import accuracy_score

# Tokenizer for data
from transformers import AutoTokenizer
# Based model
from transformers import T5Config, T5ForConditionalGeneration, T5Tokenizer

# Used for progress
from tqdm import tqdm

# Importing dataset class
from qg_dataset import CustomQGDataset

# TODO
from accuracy_score import AccuracyScore


def get_tokenizer(checkpoint: str) -> T5Tokenizer:
    """
    Fetches the Tokenizer from the transformer library.
    Parameters
    ----------
    checkpoint:str
        use Checkpoint to fetch Tokenizer
    Returns
    -------
    T5Tokenizer
        Used Tokenizer for the model.
    """
    fetched_tokenizer = T5Tokenizer.from_pretrained(checkpoint)
    fetched_tokenizer.add_special_tokens(
        {'additional_special_tokens': ['<ANWSR>', '<CNTXT>']}
    )
    return fetched_tokenizer


# Put functions into class to make it easily accessible from different python files
class ModelTrainer:
    def __init__(
            self,
            training_dataset: Dataset,
            validation_dataset: Dataset,
            checkpoint: str,
            model=None,
            tokenizer=None) -> None:

        # setup starting checkpoint
        self.checkpoint = checkpoint

        # Set device to use CUDA if available during use
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        # setup tokenizer
        self.tokenizer = get_tokenizer() if tokenizer is None else tokenizer
        # setup
        self.model = self._get_starting_model() if model is None else model

        # limits epochs for training
        self.epochs = 20

        # folder to save model
        self.save_dir = "./qg_model"

        # setup batch sizes (tuned down because training is highly resource intensive on the pu)
        self.train_batch_size = 4
        self.valid_batch_size = 32

        # Create DataLoader instances to fetch data for training and testing
        self.training_data_loader = DataLoader(
            training_dataset,
            batch_size=self.train_batch_size,
            num_workers=2,
            shuffle=True
        )
        self.testing_data_loader = DataLoader(
            validation_dataset,
            batch_size=self.train_batch_size,
            num_workers=2,
            shuffle=False
        )

        # Define which optimizer to use
        # AdamW is an optimized stochastic gradient descent (https://pytorch.org/docs/stable/optim.html#algorithms)
        self.optimizer = AdamW(self.model.parameters(), lr=1e-3)

        # setup loss measurement for training
        self.train_loss = AccuracyScore()

        # setup accuracy storage for validation
        self.best_accuracy = 0

    # Default training method
    def train(self) -> None:
        for epoch in range(1, self.epochs + 1):
            self.model.train()
            self.train_loss.reset()

            with tqdm(total=len(self.train_loader), unit="batches") as epochs:
                # using tqdm for a progress bar for sanity
                epochs.set_description(f"Training epoch: {epoch}")

                # Iterate over loaded data
                for data in self.train_loader:
                    # standard optimizer step from pytorch
                    self.optimizer.zero_grad()
                    data = {key: value.to(self.device) for key, value in data.items()}
                    output = self.model(**data)
                    loss = output.loss
                    loss.backward()
                    self.optimizer.step()
                    self.train_loss.update(loss.item(), self.train_batch_size)

                    # progressing to next epoch and updating the status bar
                    # putting the training loss as additional information at the end of the status bar
                    epoch.set_postfix({"train_loss": self.train_loss.avg})
                    # manually incrementing the epoch counter by 1
                    epoch.update(1)

            # Validating training step
            new_accuracy = self.evaluate_accuracy(self.valid_loader)
            if new_accuracy > self.best_accuracy:
                print(f"""Accuracy on Validation dataset improved from 
                {self.best_accuracy:.3f} to {new_accuracy:.3f}.
                Saving model to drive.""")
                self.best_accuracy = new_accuracy
                self._save()
            else:
                print("Model didnt improve on previous accuracy; discarding this generation")

    # prohibiting learning on the validation dataset
    @torch.no_grad()
    def evaluate_accuracy(self, dataloader: DataLoader) -> float:
        """
        Function to evaluate the model based on accuracy.
        Parameters
        ----------
        dataloader : DataLoader
            DataLoader object from which to load the data.

        Returns
        -------
        float
            Average accuracy during validation.
        """
        # calls eval function from the model
        self.model.eval()
        accuracy = AccuracyScore()

        # create new status bar for the validation progress
        with tqdm(total=len(dataloader), unit="batches") as epoch:
            epoch.set_description("Validation")
            for data in dataloader:
                # package data into dictionary for model to interpret
                data = {key: value.to(self.device) for key, value in data.items()}
                # put data into model and fetch output
                output = self.model(**data)
                # evaluate output based on argmax function on output layer
                predictions = torch.argmax(output.logits, dim=1)

                # calculate and update score
                score = accuracy_score(data["labels"].cpu(), predictions.cpu())
                accuracy.update(score, self.valid_batch_size)

                # progress to next epoch
                epoch.set_postfix({"Accuracy on validation data": round(accuracy.avg, 3)})
                epoch.update(1)
        return accuracy.avg

    def _save(self) -> None:
        """
        Private method to save the model during each step for safety.
        """
        self.tokenizer.save_pretrained(self.save_dir)
        self.model.save_pretrained(self.save_dir)

    def _get_starting_model(self) -> T5ForConditionalGeneration:
        """
        Sets up the base model on which the question generator is based on.
        Returns
        -------
        T5ForConditionalGeneration
        """
        config = T5Config(decoder_start_token_id=self.tokenizer.pad_token_id)
        model = T5ForConditionalGeneration(config).from_pretrained(self.checkpoint)
        model.resize_token_embeddings(len(self.tokenizer))
        model = model.to(self.device)
        return model


if __name__ == "__main__":
    tokenizer = get_tokenizer("t5-base")

    dataset = datasets.load_dataset("Sabokou/qg_squad_modified")

    train_set = CustomQGDataset(dataset["train"], max_length=512, pad_mask_id=-100, tokenizer=tokenizer)
    valid_set = CustomQGDataset(dataset["validation"], max_length=512, pad_mask_id=-100, tokenizer=tokenizer)

    trainer_class = ModelTrainer(training_dataset=train_set, validation_dataset=valid_set, checkpoint="t5-base")
    trainer_class.train()