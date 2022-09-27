"""This module contains MNIST DataModule
"""
import pathlib
from typing import Union

from torch.utils.data import DataLoader, random_split
from torchvision import transforms
from torchvision.datasets import MNIST

from digit_recognizer.config import DATA_PATH
from digit_recognizer.datamodule.interface import DataModule_Interface
from digit_recognizer.dataset.kaggle_mnist import KaggleMNISTDataset


class MNISTDataModule(DataModule_Interface):
    """
    LightningDataModule for MNIST dataset
    """

    def __init__(
        self,
        data_dir: Union[pathlib.Path, str] = DATA_PATH,
        batch_size: int = 32,
        val_split: float = 0.2,
    ) -> None:
        """
        Args:
            data_dir (str, optional): Download Data Directory. Defaults to "./data".
            batch_size (int, optional): Batch Size used to DataLoader. Defaults to 32.
            val_split (float, optional): Percentage Split between train_dataset and val_dataset. Defaults to 0.2.
        """
        super(MNISTDataModule, self).__init__(data_dir, batch_size, val_split)

        self.transforms = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize(
                    (0.5),
                    (0.5),
                ),
            ]
        )

    def prepare_data(self) -> None:
        """
        Download/Load data to self.data_dir
        """
        MNIST(self.data_dir, download=True, train=True)
        MNIST(self.data_dir, download=True, train=False)

    def setup(self, stage: str) -> None:
        """_summary_

        Args:
            stage (str): "fit" or "test". Stage "fit" will split full train dataset into train set and validation set
            and store both datasets as class instances attributes. Stage "test" will return full test dataset.
        """
        if stage == "fit":

            self.mnist_full = MNIST(
                self.data_dir, train=True, transform=self.transforms
            )

            self.mnist_train, self.mnist_val = random_split(
                self.mnist_full, [50000, 10000]
            )

        if stage == "test":
            self.mnist_test = MNIST(
                self.data_dir, train=False, transform=self.transforms
            )

    def train_dataloader(self) -> DataLoader:
        """
        Return Train DataLoader using specified batch_size
        """
        return DataLoader(self.mnist_train, batch_size=self.batch_size)

    def val_dataloader(self) -> DataLoader:
        """
        Return Validation DataLoader using specified batch_size
        """
        return DataLoader(self.mnist_val, batch_size=self.batch_size)

    def test_dataloader(self) -> DataLoader:
        """
        Return Test DataLoader using specified batch_size
        """
        return DataLoader(self.mnist_test, batch_size=self.batch_size)


class KaggleMNISTDataModule(MNISTDataModule):
    """
    LightningDataModule for Kaggle MNIST dataset
    """

    def __init__(
        self,
        data_dir: Union[pathlib.Path, str] = DATA_PATH / "Kaggle",
        batch_size: int = 32,
        val_split: float = 0.2,
    ) -> None:
        """
        Args:
            data_dir (str, optional): Download Data Directory. Defaults to "./data".
            batch_size (int, optional): Batch Size used to DataLoader. Defaults to 32.
            val_split (float, optional): Percentage Split between train_dataset and val_dataset. Defaults to 0.2.
        """
        super(MNISTDataModule, self).__init__(data_dir, batch_size)
        self.transforms = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize(
                    (0.5),
                    (0.5),
                ),
            ]
        )

    def setup(self, stage: str) -> None:
        """_summary_

        Args:
            stage (str): "fit" or "test". Stage "fit" will split full train dataset into train set and validation set
            and store both datasets as class instances attributes. Stage "test" will return full test dataset.
        """
        if stage == "fit":

            self.mnist_full = KaggleMNISTDataset(
                self.data_dir, train=True, transform=self.transforms
            )

            ds_len = len(self.mnist_full)
            self.mnist_train, self.mnist_val = random_split(
                self.mnist_full,
                [int(ds_len * (1 - self.val_split)), int(ds_len * self.val_split)],
            )

        if stage == "test":
            self.mnist_test = KaggleMNISTDataset(
                self.data_dir, train=False, transform=self.transforms
            )
