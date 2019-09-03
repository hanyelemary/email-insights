import sys
import zipfile
import mailparser
import csv
import os.path
import re
import json
from lxml import etree
from datetime import datetime


def load_attachment(zip, name):
    fh = zip.open(name)
    return fh


def get_id(email):
    tag_id = email.find('.//OPFMessageCopyMessageID')
    if tag_id is None:
        tag_id = email.find('.//OPFMessageCopyExchangeConversationId')
    return tag_id.text.strip()


def get_date(email):
    tag = email.find('.//OPFMessageCopySentTime')
    if tag is None:
        tag = email.find('.//OPFMessageCopyReceivedTime')
    date = datetime.strptime(tag.text.strip(), '%Y-%m-%dT%H:%M:%S')
    return date.isoformat()


def remove_tags(text):
    TAG_RE = re.compile(r'<[^>]+>')
    return TAG_RE.sub('', text)


def remove_line_breaks(text):
    return text.replace('\n', '')


def remove_nbsp(text):
    return text.replace('&nbsp;', '')


def get_body(email, strip_xml_tags):
    has_html = email.find('.//OPFMessageGetHasHTML')
    tag_body = email.find('.//OPFMessageCopyBody')
    mime_type = 'text/plain'
    if has_html is not None:
        html = has_html.text.replace('E0', '')
        if html == '1':
            tag_body = email.find('.//OPFMessageCopyHTMLBody')
            mime_type = 'text/html'

    body = None
    if tag_body is not None:
        body = tag_body.text

    if body is not None:
        if body.strip() is not None:
            body = body.strip()

            if strip_xml_tags is True:
                body = remove_tags(body)
                body = remove_line_breaks(body)
                body = remove_nbsp(body)

    return body


def get_attachments(zip, email):
    attachments = []
    tag_attachments = email.find('.//OPFMessageCopyAttachmentList')
    if tag_attachments is not None:
        for attachment in tag_attachments.findall('.//messageAttachment'):
            name = attachment.get('OPFAttachmentName')
            mime_type = attachment.get('OPFAttachmentContentType')
            # extension = attachment.get('OPFAttachmentContentExtension')
            # id = attachment.get('OPFAttachmentContentID')
            file = {
                'file_name': name,
                'mime_type': mime_type
            }
            url = attachment.get('OPFAttachmentURL')
            if url is not None:
                fh = load_attachment(zip, url)
                file['file_path'] = url
                file['file_handle'] = fh
            attachments.append(file)
    return attachments


def get_addresses(email):
    tag_from = email.find('.//OPFMessageCopyFromAddresses')
    tag_sender = email.find('.//OPFMessageCopySenderAddress')
    tag_to = email.find('.//OPFMessageCopyToAddresses')
    tag_cc = email.find('.//OPFMessageCopyCCAddresses')
    tag_bcc = email.find('.//OPFMessageCopyBCCAddresses')

    from_names, from_emails = get_contacts(tag_from)
    sender_names, sender_emails = get_contacts(tag_sender)
    to_names, to_emails = get_contacts(tag_to)
    cc_names, cc_emails = get_contacts(tag_cc)
    bcc_names, bcc_emails = get_contacts(tag_bcc)

    names = to_names + from_names + cc_names + bcc_names + sender_names
    emails = to_emails + from_emails + cc_emails + bcc_emails + sender_emails

    frm = from_emails + sender_emails
    author = from_names + sender_names

    return names, emails, author, frm, to_emails, cc_emails, bcc_emails


def get_contacts(addresses):
    names = []
    emails = []
    if addresses is not None:
        for address in addresses.findall('.//emailAddress'):
            email = address.get('OPFContactEmailAddressAddress')
            if email is not None:
                emails.append(email)
            name = address.get('OPFContactEmailAddressName')
            if name is not None and name != email:
                names.append(name)

    return names, emails


def parse_message(zip, name, strip_xml_tags):
    headers = {
        'From': None,
        'To': None,
        'Subject': None,
        'Message-ID': None,
        'CC': None,
        'BCC': None,
        'Date': None,
    }
    body = None
    attachments = []
    names = []
    emails = []
    title = None
    author = None

    doc = None
    fh = zip.open(name)

    try:
        doc = etree.parse(fh)
    except etree.XMLSyntaxError:
        p = etree.XMLParser(huge_tree=True)
        try:
            doc = etree.parse(fh, p)
        except etree.XMLSyntaxError:
            # probably corrupt
            pass

    if doc is None:
        return

    for email in doc.findall('//email'):
        headers['Message-ID'] = get_id(email)
        headers['Date'] = get_date(email)

        tag_subject = email.find('.//OPFMessageCopySubject')
        # OPFMessageCopyThreadTopic
        if tag_subject is not None:
            headers['Subject'] = title = tag_subject.text.strip()

        names, emails, author, frm, to, cc, bcc = get_addresses(email)
        headers['To'] = to
        headers['From'] = frm
        headers['CC'] = cc
        headers['BCC'] = bcc

        body = get_body(email, strip_xml_tags)

        return {
            'headers': headers,
            'body': body,
            'attachments': attachments,
            'names': names,
            'emails': emails,
            'title': title,
            'author': author,
            'created_at': headers['Date']
        }

def convert_to_csv(filename, record):
    headers = ['from', 'to', 'author', 'subject', 'body', 'created_at']
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', lineterminator='\n')

        if not file_exists:
            writer.writerow(headers) # write the header

        writer.writerow([
            record['headers']['From'],
            record['headers']['To'],
            record['author'],
            record['title'],
            record['body'],
            record['created_at']
        ])

    csvfile.close()

def main():
    fn = sys.argv[1]
    zf = zipfile.ZipFile(fn, 'r')

    for info in zf.namelist():
        if 'com.microsoft.__Attachments' in info:
            continue
        if 'message_' not in info:
            continue

        with open('config.json') as json_config:
            config = json.load(json_config)

        strip_xml_tags = config['strip_xml_tags']

        csv_file = config['filename']
        record = parse_message(zf, info, strip_xml_tags)
        convert_to_csv(csv_file, record)

if __name__ == '__main__':
    main()
