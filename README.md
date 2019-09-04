# Email Insights
Unsupervised learning (clustering) to provide insights on exported emails.

## Prerequisites:
* [Python 3.7](https://www.python.org/downloads/release/python-370/)
* [Virtual Env](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

## Getting started:
Export emails into csv. At this point, we look at the subject of email. We can change it to work with email bodies as well.

The csv file must include **subject** (and **body** if you decide to go with the body) header(s). The one I'm testing with has the following:
```javascript
['from', 'to', 'author', 'subject', 'body', 'created_at']
````

### Create config json
```javascript
{
  "filename": "emails.csv",
  "strip_xml_tags": true,
  "stopwords": [
    "jira",
    "accepted",
    "nan",
    "zoom",
    "pm",
    "modernization"
  ]
}
```
*NOTE*: you can adjust any of the fields above.
> **filename**: exported csv email file

> **stopwords**: an array of words to filter out, in addition to other base english words such as: the, off, a, an ...

> **strip_xml_tags**: whether to strip xml/html tags off the email body.

### OLM to CSV conversion
This *only* applies if your exported email list is in .olm format and not in .csv

```
python olm-to-csv.py <olm_file_name>
```
> This will output a csv file based on your json config above (emails.csv) in the same working directory. It could take some time based on how many emails you have.

### Create virtual env

```
cd email-insights
virtualenv env
```

### Activate virtual env

```
source env/bin/activate
```

### Download Dependencies

```
pip install -r requirements.txt
```

### Run
```
python insights.py
```
