# Copyright © 2020 Siftrics
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__version__ = '1.0.1'

import base64
import requests
import time

def _getOrElse(json, key):
    if key not in json:
        raise Exception('This should never happen. Got successful HTTP status code (200) but the body was not the JSON we were expecting.')
    return json[key]

class Client:
    def __init__(self, api_key):
        self.api_key = api_key

    def doPoll(self, pollingURL, files):
        fileIndex2HaveSeenPages = [list() for _ in files]
        while True:
            response = requests.get(
                pollingURL,
                headers={ 'Authorization': 'Basic {}'.format(self.api_key) },
            )
            response.raise_for_status()
            json = response.json()
            pages = _getOrElse(json, 'Pages')
            if not pages:
                time.sleep(0.5)
                continue
            for page in pages:
                fileIndex = _getOrElse(page, 'FileIndex')
                pageNumber = _getOrElse(page, 'PageNumber')
                numberOfPagesInFile = _getOrElse(page, 'NumberOfPagesInFile')
                if not fileIndex2HaveSeenPages[fileIndex]:
                    fileIndex2HaveSeenPages[fileIndex] = [False]*numberOfPagesInFile
                fileIndex2HaveSeenPages[fileIndex][pageNumber-1] = True
            yield json['Pages']
            haveSeenAllPages = True
            for l in fileIndex2HaveSeenPages:
                if not l:
                    haveSeenAllPages = False
                    break
                if not all(l):
                    haveSeenAllPages = False
                    break
            if haveSeenAllPages:
                return
            time.sleep(0.5)

    def recognizeAsGenerator(self, files):
        payload = { 'files': [] }
        for f in files:
            if f.endswith('.pdf'):
                mimeType = 'application/pdf'
            elif f.endswith('.bmp'):
                mimeType = 'image/bmp'
            elif f.endswith('.gif'):
                mimeType = 'image/gif'
            elif f.endswith('.jpeg'):
                mimeType = 'image/jpeg'
            elif f.endswith('.jpg'):
                mimeType = 'image/jpg'
            elif f.endswith('.png'):
                mimeType = 'image/png'
            else:
                msg = '{} does not have a valid extension; it must be one of ".pdf", ".bmp", ".gif", ".jpeg", ".jpg", or ".png".'.format(f)
                raise Exception(msg)
            with open(f, 'rb') as fileObj:
                base64File = base64.b64encode(fileObj.read())
            payload['files'].append({
                'mimeType': mimeType,
                'base64File': base64File.decode('utf-8'),
            })
        response = requests.post(
            'https://siftrics.com/api/sight/',
            headers={ 'Authorization': 'Basic {}'.format(self.api_key) },
            json=payload,
        )
        response.raise_for_status()
        json = response.json()
        if 'PollingURL' in json:
            for pages in self.doPoll(json['PollingURL'], files):
                yield pages
            return
        if 'RecognizedText' not in json:
            raise Exception('This should never happen. Got successful HTTP status code (200) but the body was not the JSON we were expecting.')
        yield [{
            'Error': '',
            'FileIndex': 0,
            'PageNumber': 1,
            'NumberOfPagesInFile': 1,
            'RecognizedText': json['RecognizedText'],
        }]

    def recognize(self, files):
        if type(files) is not list:
            msg = 'You must pass in a list of files, not a {}'.format(type(files))
            raise TypeError(msg)
        pages = list()
        for ps in self.recognizeAsGenerator(files):
            pages.extend(ps)
        return pages
