"""Filtering for OSCAR v1."""

import argparse

from datasets import load_dataset

from oscar_sample_filter import OscarFiltering


def parseArgs():
    parser = argparse.ArgumentParser(description="Filtering for OSCAR v1.")
    parser.add_argument(
        "--dataset_name",
        type=str,
        default="oscar",
        help="Name of the dataset to load.",
    )
    parser.add_argument(
        "--config_name",
        type=str,
        default="unshuffled_deduplicated_af",
        help="Name of the dataset config to pass.",
    )
    parser.add_argument(
        "--data_files",
        type=str,
        default=None,
        help="'load_dataset' returns all files that match the Unix style pattern passed by 'data_files'",
    )
    parser.add_argument(
        "--lang_oscar_id",
        type=str,
        default="af",
        help="ID of the language in which the dataset is written.",
    )
    parser.add_argument(
        "--path_fasttext_model",
        type=str,
        default="/tmp/lid.176.bin",
        help="Path to the Fasttext model used for language identification.",
    )
    parser.add_argument(
        "--path_kenlm_model",
        type=str,
        default="ac_dc/af.arpa.bin",
        help="Path to the KenLM model used to compute perplexity scores.",
    )
    parser.add_argument(
        "--path_sentence_piece_model",
        type=str,
        default="ac_dc/af.sp.model",
        help="Path to the Sentence Piece model used to tokenize text for perplexity scores.",
    )
    parser.add_argument(
        "--num_proc",
        type=int,
        default=2,
        help="Number of processes for multiprocessing.",
    )
    parser.add_argument(
        "--path_dir_save_oscar",
        type=str,
        default="../Oscar_filtered/",
        help="Path to the directory where the filtered version of Oscar will be saved.",
    )
    args = parser.parse_args()
    return args


def main():
    args = parseArgs()

    dataset = load_dataset(
        args.dataset_name,
        args.config_name,
        data_files=args.data_files,
        split="train",
    )

    oscar_filtering = OscarFiltering(
        dataset=dataset,
        lang_oscar_id=args.lang_oscar_id,
        path_fasttext_model=args.path_fasttext_model,
        path_kenlm_model=args.path_kenlm_model,
        path_sentence_piece_model=args.path_sentence_piece_model,
        num_proc=args.num_proc,
        path_dir_save_oscar=args.path_dir_save_oscar,
    )
    oscar_filtering.modifying_sentences()
    oscar_filtering.filtering()
    oscar_filtering.save_dataset()


if __name__ == "__main__":
    main()
