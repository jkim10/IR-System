# SpanBERT for Relation Extraction from Web Documents
By Justin Kim(jyk2149) and Mavis Athene U Chen(mu2288)

## Files in Submission
- requirements.txt
- extract.py
- README.md

## How to Run

```bash
pip3 install -r requirements.txt
bash download_finetuned.sh
python3 extract.py <google api key> <google engine id> <r> <t> <q> <k>
```
Google API KEY: AIzaSyC6uXsEBblG4JwiO7X25rG5RDUdQrOmrkc

Google Search Engine ID: db7c825fd9c7885a2

Sample Run with Above API Key and Engine Key:

```bash
python3 extract.py AIzaSyC6uXsEBblG4JwiO7X25rG5RDUdQrOmrkc db7c825fd9c7885a2 4 .7 "bill gates microsoft" 10
```


## Internal Design


## Description of "Step 3"

