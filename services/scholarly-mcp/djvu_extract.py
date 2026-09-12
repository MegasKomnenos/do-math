"""Mechanical DjVu page reads using an isolated, pinned DjVuLibre build."""
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile

from scholarly import ServiceError

RUNTIME=Path(__file__).resolve().parent/'data/tools/djvulibre/runtime'


def validate_document(data):
    if len(data)<16 or data[:8]!=b'AT&TFORM' or data[12:16] not in (b'DJVU',b'DJVM',b'PM44',b'BM44'):
        raise ServiceError('invalid_document','The artifact is not a standalone DjVu document')
    end=12+struct.unpack('>I',data[8:12])[0]
    if end<16 or end>len(data) or len(data)>end+1 or data[end:] not in (b'',b'\0'):
        raise ServiceError('invalid_document','DjVu container length does not match its bytes')
    chunks=[];position=16
    while position<end:
        if position+8>end:raise ServiceError('invalid_document','DjVu chunk header is truncated')
        size=struct.unpack('>I',data[position+4:position+8])[0];stop=position+8+size
        if stop>end:raise ServiceError('invalid_document','DjVu chunk extends beyond its container')
        chunks.append((data[position:position+4],data[position+8:stop]))
        position=stop+(size%2 if stop<end else 0)
    if data[12:16]==b'DJVM':
        if chunks and chunks[0][0]==b'DIR0':
            return  # Upstream OLD_BUNDLED resolves components only within this file.
        directories=[value for name,value in chunks if name==b'DIRM']
        if len(directories)!=1 or len(directories[0])<3 or chunks[0][0]!=b'DIRM':
            raise ServiceError('invalid_document','DjVu multipage document has no unique directory')
        if not directories[0][0]&0x80:
            raise ServiceError('external_document_components','The indirect DjVu document needs external component files; preserved bytes remain available',status='unsupported')
    elif any(name in (b'INCL',b'NDIR') for name,_ in chunks):
        raise ServiceError('external_document_components','The single-page DjVu refers to an external component; preserved bytes remain available',status='unsupported')


def decoder_path(tool):
    if tool not in ('djvutxt','djvused','ddjvu'):
        raise ServiceError('invalid_decoder','Unknown DjVu operation')
    name=tool+('.exe' if os.name=='nt' else '')
    try:
        path=RUNTIME/name;manifest=json.loads((RUNTIME/'provenance.json').read_text(encoding='utf-8'))
        if hashlib.sha256(path.read_bytes()).hexdigest()!=manifest['tools'][name]['sha256']:
            raise ValueError
    except (OSError,ValueError,KeyError):
        raise ServiceError('decoder_not_available','Build the pinned local DjVu tools with setup_djvu.py; original artifact remains preserved',status='not_implemented') from None
    return path


def run_decoder(tool,args,folder):
    executable=decoder_path(tool)
    try:
        result=subprocess.run([str(executable),*map(str,args)],cwd=folder,capture_output=True,
            timeout=30,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    except subprocess.TimeoutExpired:
        raise ServiceError('document_decode_timeout','DjVu decoding exceeded the per-page time limit') from None
    except OSError:
        raise ServiceError('decoder_not_available','The verified DjVu decoder could not start',status='not_implemented') from None
    if result.returncode:
        raise ServiceError('invalid_document','DjVu decoding failed',decoder=tool,exit_code=result.returncode)
    return result.stdout


def read_page(store,meta,document,folder,index,render):
    try:
        text=run_decoder('djvutxt',[f'--page={index+1}',document],folder).decode('utf-8')
    except UnicodeDecodeError:
        raise ServiceError('invalid_document','DjVu text layer did not decode as UTF-8') from None
    row={'page':index+1,'text':text,'text_layer_empty':not text.strip()}
    if render or not text.strip():
        raw=run_decoder('ddjvu',['-format=ppm',f'-page={index+1}','-size=1600x2000',document],folder)
        try:
            import pymupdf
            image=pymupdf.Pixmap(raw)
            png=image.tobytes('png')
        except Exception:
            raise ServiceError('invalid_document','DjVu decoder returned no readable page image') from None
        row['image']=store.put(png,'image/png',meta['source'],meta['url'],parent_ref=meta['ref'],page=index+1,
            role='document_page',decoder='DjVuLibre',width=image.width,height=image.height)
    return row


def pages(store,meta,data,*,start,count,render):
    validate_document(data)
    ref=meta['ref'];rows=[];errors=[]
    with tempfile.TemporaryDirectory(prefix='scholarly-djvu-') as temp:
        folder=Path(temp);document=folder/'input.djvu';document.write_bytes(data)
        raw_total=run_decoder('djvused',[document,'-e','n'],folder).strip()
        if not raw_total.isdigit() or int(raw_total)<1:
            raise ServiceError('invalid_document','DjVu decoder returned no valid page count')
        total=int(raw_total)
        for index in range(start,min(start+count,total)):
            try:
                row=read_page(store,meta,document,folder,index,render)
            except ServiceError as error:
                if not rows:raise
                errors.append({'page':index+1,**error.result});break
            rows.append(row)
    return {'status':'partial' if errors else 'ok','artifact':ref,'unit':'pages','start':start,'total':total,'returned':len(rows),
        'next_start':start+len(rows) if start+len(rows)<total else None,'items':rows,
        **({'errors':errors} if errors else {}),
        'interpretation':'Stored DjVu text layer and mechanical page rendering; no new OCR or image interpretation is performed'}
