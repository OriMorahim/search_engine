import os
import glob
import pandas as pd

RELEVANT_COLUMS = ["tweet_id", "full_text"]

class ReadFile:
    def __init__(self, corpus_path):
        self.corpus_path = corpus_path

    def read_and_concat_all_parquet_in_dir(self):
        """
        This method used to read all the parquet files in a directory. The directory
        we fetch the files from is corpus_path
        :return:
        """
        files = glob.glob(f"{self.corpus_path}/*.parquet")

        dfs = []
        for file in files:
            dfs.append(pd.read_parquet(file))

        return pd.concat(dfs, axis=0)

    def read_and_concat_all_parquet_in_dir_of_dirs(self, max_files=100):
        """
        This method used to read all parquet files from a directory of directories. The directory
        we fetch the files from is corpus_path
        :return:
        """
        dfs = []
        counter = 0
        for dir in os.listdir(self.corpus_path):
            files = glob.glob(f"{self.corpus_path}/{dir}/*.parquet")
            for file in files:
                dfs.append(pd.read_parquet(file, columns=RELEVANT_COLUMS))
                counter += 1
                if counter >= max_files:
                    break
            if counter >= max_files:
                break
        return pd.concat(dfs, axis=0)

