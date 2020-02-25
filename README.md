This repository contains the official [Sight API](https://siftrics.com/) Python client. The Sight API is a text recognition service.

# Quickstart

1. Install the package.

```
pip install sight-api
```

or

```
poetry add sight-api
```

etc.

2. Grab an API key from the [Sight dashboard](https://siftrics.com/).
3. Create a client, passing your API key into the constructor, and recognize text:

```
import sight_api

client = sight_api.Client('xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx')

pages = client.recognize(['invoice.pdf', 'receipt_1.png'])
```

`pages` looks like this:

```
[
    {
        "Error": "",
        "FileIndex": 0,
        "PageNumber": 1,
        "NumberOfPagesInFile": 3,
        "RecognizedText": [ ... ]
    },
    ...
]
```

`FileIndex` is the index of this file in the original request's "files" array.

`RecognizedText` looks like this:

```
"RecognizedText": [
    {
        "Text": "Invoice",
        "Confidence": 0.22863210084975458
        "TopLeftX": 395,
        "TopLeftY": 35,
        "TopRightX": 449,
        "TopRightY": 35,
        "BottomLeftX": 395,
        "BottomLeftY": 47,
        "BottomRightX": 449,
        "BottomRightY": 47,
    },
    ...
]
```

## Streaming in Results

If you process more than one page in a single `.recognize([ ... ])` call, results may come in over time, instead of all at once.

To access results (`pages` objects) as soon as they come in, there is a generator you can use:

```
for pages in self.recognizeAsGenerator(['invoice.pdf', 'receipt_1.png']):
    print(pages)
```

In fact, `.recognize([ ... ])` is defined in terms of that generator:

```
class Client:
    ...
    def recognize(self, files):
        ...
        pages = list()
        for ps in self.recognizeAsGenerator(files):
            pages.extend(ps)
        return pages
```

Here is the [official documentation for the Sight API](https://siftrics.com/docs/sight.html).

# Apache V2 License

This code is licensed under Apache V2.0. The full text of the license can be found in the "LICENSE" file.