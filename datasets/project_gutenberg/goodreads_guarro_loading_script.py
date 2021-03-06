import datasets
import pathlib
import sqlite3
import configparser

# TODO: Add BibTeX citation
# Find for instance the citation on arxiv or on the dataset repo/website
_CITATION = """\
@InProceedings{huggingface:dataset,
title = {A great new dataset},
author={huggingface, Inc.
},
year={2020}
}
"""

# TODO: Add description of the dataset here
# You can copy an official description
_DESCRIPTION = """\
GoodReads dataset generated by ***this paper***
"""

try:
  import google.colab
  IN_COLAB = True
except:
  IN_COLAB = False

config = configparser.ConfigParser()

if IN_COLAB:
    config.read(r'/content/drive/MyDrive/Thesis/BookSuccessPredictor/config.ini')
else:
    config.read(r'C:\Users\lucag\Google Drive\Thesis\BookSuccessPredictor\config_local.ini')

preprocess_dir = 'nered' if eval(config['Model']['use_ner']) else 'trimmed'
print('Using preprocess dir:', preprocess_dir)

basepath = pathlib.Path(config['Datasets']['goodreads_guarro_path'])

# TODO: Name of the dataset usually match the script name with CamelCase instead of snake_case
class GoodReadsPracticeDataset(datasets.GeneratorBasedBuilder):
    """TODO: Short description of my dataset."""

    VERSION = datasets.Version("1.1.0")

    # This is an example of a dataset with multiple configurations.
    # If you don't want/need to define several sub-sets in your dataset,
    # just remove the BUILDER_CONFIG_CLASS and the BUILDER_CONFIGS attributes.

    # If you need to make complex sub-parts in the datasets with configurable options
    # You can create your own builder configuration class to store attribute, inheriting from datasets.BuilderConfig
    # BUILDER_CONFIG_CLASS = MyBuilderConfig

    # You will be able to load one or the other configurations in the following list with
    # data = datasets.load_dataset('my_dataset', 'first_domain')
    # data = datasets.load_dataset('my_dataset', 'second_domain')
    BUILDER_CONFIGS = [
        datasets.BuilderConfig(name="main_domain", version=VERSION, description="This is the original source of the GoodReads dataset")
    ]

    # genre_mapper = {'Detective_and_mystery_stories', 'Drama', 'Fiction', 'Historical_fiction', 'Love_stories', 'Poetry', 'Science_fiction', 'Short_stories'}

    def _info(self):
        # TODO: This method specifies the datasets.DatasetInfo object which contains informations and typings for the dataset
        features = datasets.Features(
            {
                "text": datasets.Value("string"),
                # These are the features of your dataset like images, labels ...
            }
        )

        return datasets.DatasetInfo(
            # This is the description that will appear on the datasets page.
            description=_DESCRIPTION,
            # This defines the different columns of the dataset and their types
            features=features,  # Here we define them above because they are different between the two configurations
            # If there's a common (input, target) tuple from the features,
            # specify them here. They'll be used if as_supervised=True in
            # builder.as_dataset.
            supervised_keys=None,
            # Citation for the dataset
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        # TODO: This method is tasked with downloading/extracting the data and defining the splits depending on the configuration
        # If several configurations are possible (listed in BUILDER_CONFIGS), the configuration selected by the user is in self.config.name

        # dl_manager is a datasets.download.DownloadManager that can be used to download and extract URLs
        # It can accept any type or nested list/dict and will give back the same structure with the url replaced with path to local files.
        # By default the archives will be extracted and a path to a cached folder where they are extracted is returned instead of the archive

        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                # These kwargs will be passed to _generate_examples
            ),
        ]

    def _generate_examples(
        self
    ):
        conn = sqlite3.connect(basepath / 'guarro_goodreads.db')
        dataCur = conn.cursor()
        dataCur.execute("Select file_path from books where use_for_adaptive_ft = 2")

        record = dataCur.fetchone()
        counter_id = 0
        while (record):
            file_path = basepath / pathlib.PureWindowsPath(record[0]).as_posix()
            nered_path = file_path.parent / 'preprocessed' / preprocess_dir / file_path.name

            data = None
            try:
                with open(nered_path, encoding='utf-8') as myfile:
                    data=myfile.read()
            except UnicodeDecodeError:
                with open(nered_path, encoding='latin-1') as myfile:
                    data=myfile.read()
            
            yield counter_id, {
                "text": data
            }
            counter_id += 1
            record = dataCur.fetchone()
