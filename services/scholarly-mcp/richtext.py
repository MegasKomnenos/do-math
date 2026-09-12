"""Mechanical RTF text extraction; embedded objects are never executed."""
import re
from scholarly import ServiceError

CONTROL=re.compile(br'\\([A-Za-z]+)(-?\d+)? ?')


def rtf_text(data):
    if not data.lstrip().startswith(br'{\rtf1'):
        raise ServiceError('invalid_document','The file does not contain an RTF document')
    # Remove exactly the declared binary bytes before a text parser sees braces
    # inside an image/object. Retain its surrounding RTF group and destination.
    output=bytearray()
    index=0
    depth=0
    ended=False
    while index<len(data):
        if ended:
            if data[index] not in b' \t\r\n\f\v\0':
                raise ServiceError('invalid_document','RTF has content after its document group')
            index+=1
            continue
        if data[index]==92:
            if index+1<len(data) and data[index+1] in b'\\{}':
                output.extend(data[index:index+2]);index+=2;continue
            control=CONTROL.match(data,index)
            if control:
                if control[1]==b'bin':
                    try:size=int(control[2])
                    except (ValueError,TypeError):
                        raise ServiceError('invalid_document','RTF binary data has an invalid byte count') from None
                    if size<0 or control.end()+size>len(data):
                        raise ServiceError('invalid_document','RTF binary data is truncated or has an invalid byte count')
                    index=control.end()+size
                    continue
                if control[1] in (b'u',b'uc'):
                    try:value=int(control[2])
                    except (ValueError,TypeError):
                        raise ServiceError('invalid_document','RTF Unicode controls require a numeric parameter') from None
                    if control[1]==b'u' and not -32768<=value<=32767:
                        raise ServiceError('invalid_document','RTF Unicode values must be signed 16-bit code units')
                    if control[1]==b'uc' and value<0:
                        raise ServiceError('invalid_document','RTF Unicode fallback length cannot be negative')
                output.extend(control[0]);index=control.end();continue
        if data[index]==123:depth+=1
        elif data[index]==125:
            depth-=1
            if depth<0:
                raise ServiceError('invalid_document','RTF has an unmatched closing group')
            ended=depth==0
        output.append(data[index]);index+=1
    if not ended or depth:
        raise ServiceError('invalid_document','RTF document groups are not closed')
    # Escaping literal high bytes lets the parser apply the active font/codepage,
    # instead of guessing one Unicode decoder for the whole document.
    encoded=re.sub(r'[\x80-\xff]',lambda match:"\\'%02x"%ord(match[0]),output.decode('latin1'))
    try:
        from striprtf.striprtf import rtf_to_text
        text=rtf_to_text(encoded,errors='strict')
        return text.encode('utf-16-le','surrogatepass').decode('utf-16-le')
    except (ValueError,LookupError):
        raise ServiceError('invalid_document','RTF text or its declared character encoding cannot be decoded') from None
