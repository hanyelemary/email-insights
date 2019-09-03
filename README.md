# Email Insights
Unsupervised learning (clustering) to provide insights on exported emails.

## Prerequisites:
* [Python 3.7](https://www.python.org/downloads/release/python-370/)
* [Virtual Env](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

## Getting started:
Export emails into csv. At this point, we look at the subject of email. We can change it to work with email bodies as well.

### Create config json
```javascript
{
  "filename": "emails.csv",
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
