# JuliaArt Says

This is a Juliart generator that creates a graphic with a snippet of wisdom
generated via a Markov Model based on some [text corpus](corpus).
We use version 0.0.13 of [juliart](https://www.github.com/vsoch/juliart).

![images/hamlet-pacifico.png](images/hamlet-pacifico.png)

 - [Usage](#usage): jump in and use the tool!
   - [Defaults](#defaults): generate an image using defaults
   - [Corpus](#corpus): specify a custom corpus
   - [Font](#font): customize the font
 - [Markov Models](#markov-models): a little bit about how we generate the text
 - [Docker](#docker): build a container instead.
 - [Needs Love](#needs-love): what I'd like to improve

You can see from the image that the defaults print a text overlay on the image
with slight transparency, so it's akin to a background. You can customize
the many [juliart](https://github.com/vsoch/juliart) parameters to tweak
this behavior, and likely I'll work on a similar example that shows
printing a single quote.


## Usage

You can see the basic usage as follows:

```bash
usage: juliasays.py [-h] {generate} ...

JuliaSet Says: wisdom embedded in Julia Sets graphics

optional arguments:
  -h, --help  show this help message and exit

actions:
  actions for juliart-says generator

  {generate}  juliart-says actions
    generate  generate a juliart-says image
```

The command of interest is "generate"

```bash
$ ./juliasays.py generate --help
usage: juliasays.py generate [-h] [--radius RADIUS] [--outfile OUTFILE]
                             [--fontsize FONTSIZE] [--xcoord XCOORD]
                             [--ycoord YCOORD] [--ca CA] [--cb CB] [--res RES]
                             [--iter ITERS] [--color {random,pattern,glow}]
                             [--rgb RGB]
                             [--theme {christmas,easter,fall,random,halloween,hanukkah,spring,summer,thanksgiving,valentine,winter}]
                             [--corpus {trump,hamlet,dr_seuss,ts_eliot}]
                             [--custom-corpus CUSTOM_CORPUS] [--no-model]
                             [--zoom ZOOM] [--size SIZE] [--alpha ALPHA]

optional arguments:
  -h, --help            show this help message and exit
  --radius RADIUS       the max radius to allow (default is 4)
  --outfile OUTFILE     the output file to save the image (defaults to
                        randomly generated png)
  --fontsize FONTSIZE   font size of text (if desired) defaults to 16
  --xcoord XCOORD       x coordinate for text (defaults to 0)
  --ycoord YCOORD       y coordinate for text (defaults to 0)
  --ca CA               the a component of the c parameter
  --cb CB               the b component of the c parameter
  --res RES             the resolution to generate (defaults to 1000)
  --iter ITERS          the number of iterations per pixel (defaults to 200)
  --color {random,pattern,glow}
                        a color pattern to follow.
  --rgb RGB             a specific rbg color, in format R,G,B
  --theme {christmas,easter,fall,random,halloween,hanukkah,spring,summer,thanksgiving,valentine,winter}
                        a theme to color the art (defaults to random colors)
  --corpus {trump,hamlet,dr_seuss,ts_eliot,office}
                        the corpus to use to generate text
  --custom-corpus CUSTOM_CORPUS
                        A custom corpus file, ending in .txt, placed in corpus
                        folder
  --no-model            Don't generate a sentence from corpus, just randomly
                        select.
  --zoom ZOOM           the level of zoom (defaults to 1.8)
  --size SIZE           the number of words to generate
  --alpha ALPHA         alpha (transparency) of the text (defaults to 40)
```

You'll notice that we largely take in the same arguments as the [juliart](https://github.com/vsoch/juliart)
module, and you can see the README there for details. The additional arguments added are to
specify a corpus, custom corpus, or choose to use a model or not.

```bash
  --corpus {trump,hamlet,dr_seuss,ts_eliot}
                        the corpus to use to generate text
  --custom-corpus CUSTOM_CORPUS
                        A custom corpus file, ending in .txt, placed in corpus
                        folder
  --no-model            Don't generate a sentence from corpus, just randomly
                        select.
```

Also note that juliart >= 0.0.14 is required.

### Defaults

By default, we will read in a corpus in the [corpus](corpus) folder and
generate a word gram (meaning an [ngram](https://en.wikipedia.org/wiki/N-gram)
made up of words as tokens) to generate a custom length of text. 

```bash
./juliasays.py generate --outfile images/defaults.png
```
![images/defaults.png](images/defaults.png)

The default corpus is Dr. Seuss, one that I generated a while back.


### Corpus

You can select any of the corpus provided in the corpus folder:

```bash
./juliasays.py generate --corpus trump --outfile images/trump.png
./juliasays.py generate --corpus ts_eliot --outfile images/ts_eliot.png
./juliasays.py generate --corpus hamlet --outfile images/hamlet.png
./juliasays.py generate --corpus the_office --outfile images/office.png
```

or specify the full path to your own custom corpus file.
For example, I've generated lines for each of the major office characters under [corpus/office](corpus/office)
And given a file `corpus/office/michael.txt` could generate a graphic like:

```bash
./juliasays.py generate --custom-corpus corpus/office/michael.txt --outfile images/michael-office.png
```

![images/micheal-office.png](images/michael-office.png)

Take a look at the [corpus/office](corpus/office) folder for all the different
characters. I've also provided the raw data files used to generate them.


### Raw Text

If you don't want to use Markov generation (and just return a random set of sentences)
you can do that too:

```bash
./juliasays.py generate --no-model
```

### Font

You can change the font to OpenSans-Regular:

```bash
./juliasays.py generate --font OpenSans-Regular --outfile images/opensans.png
```

![images/opensans.png](images/opensans.png)


## Markov Models

I really love this model because it's so simple to work with! We basically generate
a lookup of words (tokens), where each index has a list of all the other words that
were found to follow it. For example:

```
blue: [one, two, three, four]
```

Would say that we parsed the text and found that the tokens "one" "two" "three" and "four"
followed the word "blue." In practice we can build this lookup fairly easily
from a raw text corpus:

```python
def generate_word_grams(text):
    """Generate a lookup of words mapped to the next occurring word, and
       we can use this to generate new text based on occurrence.
    """
    words = text.split()
    wordgrams = {}

    # Add each word to the lookup
    for i in range(len(words) - 1):

        if words[i] not in wordgrams:
            wordgrams[words[i]] = []

        # Each entry should have the next occurring word
        wordgrams[words[i]].append(words[i + 1])

    return wordgrams
```

I removed some of the subtle details, like creating an empty list potentially for
the last word, and making the word lowercase to streamline the lookup.

Once we have this lookup we can generate some new sentence / text of a particular
length simply by starting with a word, and the randomly selecting some following 
word from the list (and continuing in that fashion until we have the total
number that we want).

```python
def generate_words_markov(corpus, size=10):
    """Generate a word lookup based on unique words, and for each
       have the values be the list of following words to choose from.
       Randomly select a next word in this fashion.
    """
    # Load filename into list of words
    text = load_corpus(corpus)

    # Generate words lookup
    grams = generate_word_grams(text)

    # Now generate the sentence of a particular size
    current = random.choice(text.split())
    result = current
    for _ in range(size):

        # Always look up entirely lowercase
        possibilities = grams[current.lower()]
        if len(possibilities) == 0:
            break
        next_word = random.choice(possibilities)
        result = "%s %s" % (result, next_word)
        current = next_word

    return result
```

I also remove some detail work like capitalizing the first and ending with
a period to simplify the example. You can see the full code in [juliasays.py](juliasays.py).

## Docker

If you want to build a Docker image to generate the images, you can do that:

```bash
$ docker build -t vanessa/juliart-says .
```

Then run the container and provide arguments as desired. You can bind a directory to
save files.

```bash
$ mkdir -p data
$ docker run -it -v $PWD/data:/data vanessa/juliart-says generate --outfile /data/office.png --corpus the_office
```

## What did I learn?

### Transparency

The coolest thing I picked up from this exercise was that to support transparency, I need
to create a second image layer, print the transparent text to it, and then combine
the base image with the text as an overlay. If you don't do this (and draw the
text onto the same image) it doesn't generate what you'd expect for transparency,
because the pixels are filled with a single transparent color without the backdrop.

### Needs Love

Currently, we use the font like a background to the image moreso than a quote
that you can read from start to finish. It might make sense
to have a mode that generates one or two sentences and then prints it cleanly
(somewhere) on the image. I think I'm going to work on a separate meme generator
(using the office and Confucius quotes) toward this goal.

### Acknowledgements

I didn't want to derive new corpus, so thank you to the following repositories for
being able to use your corpus / share raw data:

 - [itsron717/markov-gen](https://github.com/itsron717/markov-gen)

All are licensed under MIT so we should be okay to share.
