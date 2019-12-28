#!/usr/bin/env python

"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from juliart.main import JuliaSet
import argparse
import random
import sys
import os

here = os.path.dirname(os.path.abspath(__file__))


def get_parser():
    parser = argparse.ArgumentParser(
        description="JuliaSet Says: wisdom embedded in Julia Sets graphics"
    )

    description = "actions for juliart-says generator"
    subparsers = parser.add_subparsers(
        help="juliart-says actions",
        title="actions",
        description=description,
        dest="command",
    )

    # Many of these are the same as for Juliart Sets
    generate = subparsers.add_parser("generate", help="generate a juliart-says image")
    generate.add_argument(
        "--radius",
        dest="radius",
        help="the max radius to allow (default is 4)",
        type=int,
        default=4,
    )

    generate.add_argument(
        "--outfile",
        dest="outfile",
        help="the output file to save the image (defaults to randomly generated png)",
        type=str,
        default=None,
    )

    generate.add_argument(
        "--fontsize",
        dest="fontsize",
        help="font size of text (if desired) defaults to 16",
        type=int,
        default=36,
    )

    generate.add_argument(
        "--font",
        dest="font",
        help="choice of font (defaults to open sans)",
        type=str,
        choices=["OpenSans-Regular", "Pacifico-Regular"],
        default="OpenSans-Regular",
    )

    generate.add_argument(
        "--xcoord",
        dest="xcoord",
        help="x coordinate for text (defaults to 0)",
        type=int,
        default=10,
    )

    generate.add_argument(
        "--ycoord",
        dest="ycoord",
        help="y coordinate for text (defaults to 0)",
        type=int,
        default=10,
    )

    generate.add_argument(
        "--ca",
        dest="ca",
        help="the a component of the c parameter",
        type=float,
        default=None,
    )

    generate.add_argument(
        "--cb",
        dest="cb",
        help="the b component of the c parameter",
        type=float,
        default=None,
    )

    generate.add_argument(
        "--res",
        dest="res",
        help="the resolution to generate (defaults to 1000)",
        type=int,
        default=1000,
    )

    generate.add_argument(
        "--iter",
        dest="iters",
        help="the number of iterations per pixel (defaults to 200)",
        type=int,
        default=200,
    )

    generate.add_argument(
        "--color",
        dest="color",
        choices=["random", "pattern", "glow"],
        help="a color pattern to follow.",
        type=str,
        default="random",
    )

    generate.add_argument(
        "--rgb",
        dest="rgb",
        help="a specific rbg color, in format R,G,B",
        type=str,
        default=None,
    )

    generate.add_argument(
        "--theme",
        dest="theme",
        choices=[
            "christmas",
            "easter",
            "fall",
            "random",
            "halloween",
            "hanukkah",
            "spring",
            "summer",
            "thanksgiving",
            "valentine",
            "winter",
        ],
        help="a theme to color the art (defaults to random colors)",
        type=str,
        default="random",
    )

    generate.add_argument(
        "--corpus",
        dest="corpus",
        choices=["trump", "hamlet", "dr_seuss", "ts_eliot"],
        help="the corpus to use to generate text",
        type=str,
        default="dr_seuss",
    )

    generate.add_argument(
        "--custom-corpus",
        dest="custom_corpus",
        help="A custom corpus file, ending in .txt, placed in corpus folder",
        type=str,
        default=None,
    )

    generate.add_argument(
        "--no-model",
        dest="no_model",
        help="Don't generate a sentence from corpus, just randomly select.",
        default=False,
        action="store_true",
    )

    generate.add_argument(
        "--zoom",
        dest="zoom",
        help="the level of zoom (defaults to 1.8)",
        type=float,
        default=1.8,
    )

    generate.add_argument(
        "--size",
        dest="size",
        help="the number of words to generate",
        type=int,
        default=500,
    )

    generate.add_argument(
        "--alpha",
        dest="alpha",
        help="alpha (transparency) of the text (defaults to 40)",
        type=int,
        default=40,
    )

    return parser


def main():
    """main is the entrypoint to the juliart client.
    """

    parser = get_parser()

    # Will exit with subcommand help if doesn't parse
    args, extra = parser.parse_known_args()

    # If the provided font doesn't end in ttf
    font = args.font
    if not args.font.endswith(".ttf"):
        font = "%s.ttf" % (font)

    # Initialize the JuliaSet
    if args.command == "generate":

        # Determine if we have a corpus or custom corpus
        corpus = args.custom_corpus or args.corpus
        text = generate_text(corpus=corpus, use_model=not args.no_model, size=args.size)

        juliaset = JuliaSet(
            resolution=args.res,
            color=args.color,
            ca=args.ca,
            cb=args.cb,
            theme=args.theme,
            rgb=args.rgb,
            iterations=args.iters,
        )
        juliaset.generate_image(zoom=args.zoom, radius=args.radius)

        # Add text, if the user wants to (args.text will be checked to be None)
        juliaset.write_text(
            text,
            fontsize=args.fontsize,
            font=font,
            xcoord=args.xcoord,
            ycoord=args.ycoord,
            rgb=(255, 255, 255, args.alpha),
        )

        juliaset.save_image(args.outfile)

    else:
        parser.print_help()


## Generation Functions


def generate_text(corpus, use_model=True, size=100):
    """Based on a corpus file prefix in "corpus" generate either word-based
       ngram (wordgram) model, or just randomly select a sentence from
       the corpus.

       Parameters
       ==========
       corpus: the prefix of the corpus file, is checked to exist
       use_model: boolean. Choose an actual sentence or generate one.
       size: The number of words to generate (only for a model).
    """
    # Get the corpus file, if it exists
    corpus = get_corpus(corpus)

    if use_model:
        return generate_words_markov(corpus, size=size)
    else:
        return select_sentence(corpus)


# Word Gram Models


def generate_word_grams(text):
    """Generate a lookup of words mapped to the next occurring word, and
       we can use this to generate new text based on occurrence.
    """
    words = text.split()
    wordgrams = {}

    # Add each word to the lookup
    for i in range(len(words) - 1):

        # Have lookup be all lowercase version
        word = words[i].lower()

        if word not in wordgrams:
            wordgrams[word] = []

        # Each entry should have the next occurring word
        wordgrams[word].append(words[i + 1])

    # The last word potentially doesn't have any following
    word = words[len(words) - 1].lower()
    if word not in wordgrams:
        wordgrams[word] = []
    return wordgrams


def select_sentence(corpus):
    """Given a corpus file, split based on sentences and randomly select
       a sentence.
    """
    text = load_corpus(corpus)
    return "%s." % random.choice(text.split(".")).strip()


def generate_words_markov(corpus, size=10):
    """Generate a word lookup based on unique words, and for each
       have the values be the list of following words to choose from.
       Randomly select a next word in this fashion. We don't
       take punctuation into account, but we do capitalize the
       first letter and end the entire thing with a period.
    """
    # Load filename into list of words
    text = load_corpus(corpus)
    words = text.split()

    # Generate words lookup
    grams = generate_word_grams(text)

    # Now generate the sentence of a particular size
    current = random.choice(words)
    result = current.capitalize()
    for _ in range(size):

        # Always look up entirely lowercase
        possibilities = grams[current.lower()]
        if len(possibilities) == 0:
            break
        next_word = random.choice(possibilities)
        result = "%s %s" % (result, next_word)
        current = next_word

    # Ensure we end in a period.
    if result[-1] in [",", "", " ", "!"]:
        result = result[:-1]

    result = "%s." % result
    return result


## Corpus Functions


def get_corpus(prefix):
    """load a corpus file from "corpus" in the same directory as this script.
       we assume a .txt extension, and return the full path to the file.
    """
    corpus_folder = os.path.join(here, "corpus")
    if not os.path.exists(corpus_folder):
        sys.exit("Missing corpus folder.")

    for corpusfile in os.listdir(corpus_folder):
        if corpusfile.startswith(prefix):
            filename = os.path.join(corpus_folder, corpusfile)
            print("Found corpus file %s" % os.path.basename(filename))
            return filename

    sys.exit("Cannot find file with prefix %s" % prefix)


def load_corpus(filename):
    """Given a filename, load the corpus to build the model. This is called by
       both generation functions.
    """
    if not os.path.exists(filename):
        sys.exit("Cannot find %s" % filename)

    # Read and get rid of newlines
    with open(filename, "r") as filey:
        text = filey.read().replace("\n", "")
    return text


if __name__ == "__main__":
    main()
