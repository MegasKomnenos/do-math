import argparse,hashlib,json,re
from pathlib import Path
import pymupdf
from collect import BASE,WORK,artifact,save_json

def suggest_region(pdf_path):
    with pymupdf.open(pdf_path) as doc:
        for pn in range(min(3,len(doc))):
            page=doc[pn];lines=[]
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    text=''.join(s['text'] for s in line['spans']).strip()
                    if text:lines.append((pymupdf.Rect(line['bbox']),text))
            # OCR PDFs split one visual line into many text-dictionary lines.
            # Join nearby fragments on the same baseline before inferring columns.
            joined=[]
            for rect,text in sorted(lines,key=lambda v:(round(v[0].y0/3),v[0].x0)):
                previous=next((i for i in range(len(joined)-1,-1,-1) if abs(joined[i][0].y0-rect.y0)<3 and -1<=rect.x0-joined[i][0].x1<=24),None)
                if previous is None:joined.append((rect,text))
                else:
                    r,t=joined[previous];joined[previous]=(r|rect,t+' '+text)
            lines=joined
            def classification_label(rect,text):
                neighbors=[(r,t) for r,t in lines if abs(r.y0-rect.y0)<3 and rect.x1-1<=r.x0<rect.x1+40]
                context=text+' '+ ' '.join(t for r,t in sorted(neighbors,key=lambda x:x[0].x0))
                return re.match(r'^Abstract\s+Devices\]',context,re.I)
            heads=[(r,t) for r,t in lines if re.match(r'^(?:ABSTRACT|Abstract|AbstracL|AbstracI)\b',t) and not classification_label(r,t) and r.y0<page.rect.height*.7]
            if not heads:continue
            head,heading=heads[0]
            near=[r for r,t in lines if head.y0<=r.y0<head.y0+80 and abs(r.x0-head.x0)<35 and len(t)>35]
            if not near:continue
            right=max(r.x1 for r in near)
            column_right=page.rect.width/2 if right<page.rect.width*.62 and head.x0<page.rect.width*.45 else page.rect.width
            column_left=page.rect.width/2 if head.x0>page.rect.width*.45 else 0
            end=[r.y0 for r,t in lines if r.y0>head.y0+15 and column_left<=r.x0<column_right and re.match(r'^(?:[KG]EY\s+.{0,3}ORDS|Key\s+Words|Keywords|Categories|CR\s+CATEGOR\w*|General\s+Terms|CCS\s+CONCEPTS|(?:\d+\.?|[IVX]+\.?)?\s*Introduction)\b',t,re.I)]
            if not end:return None
            bottom=min(end)-2
            selected=[r for r,t in lines if head.y0-.5<=r.y0<bottom and column_left<=r.x0<column_right]
            if not selected:continue
            rect=pymupdf.Rect(max(0,min(r.x0 for r in selected)-2),max(0,head.y0-2),min(page.rect.width,max(r.x1 for r in selected)+2),bottom)
            if rect.height<=15 or rect.width<=30:continue
            return {'page':pn+1,'bbox_points':list(rect),'boundary_basis':'Explicit Abstract heading to next keyword/classification/Introduction heading; proposed geometry still requires visual review'}
    return None

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=0);args=ap.parse_args();items=[]
    for path in sorted((WORK/'results').glob('*.json')):
        r=json.loads(path.read_text());a=r['abstract'];f=r['fulltext']
        if f['status']!='found' or a['status']=='not_found' or a.get('extraction_quality') in {'visually_corrected','source_region_verified'}:continue
        if a['status']=='found' and 'pdf' not in a.get('source_kind','').lower():continue
        source=f['artifacts'][0];pdf=BASE/source['path'];region=suggest_region(pdf)
        if not region:continue
        with pymupdf.open(pdf) as doc:data=doc[region['page']-1].get_pixmap(matrix=pymupdf.Matrix(3,3),clip=pymupdf.Rect(region['bbox_points'])).tobytes('png')
        ar=artifact(r['paper_id'],'abstract-source-region.png',data,source['url'],'image/png')
        ar['source_region']={'pdf':source['path'],'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'page':region['page'],'bbox_points':region['bbox_points']}
        items.append({'paper_id':r['paper_id'],'title':r['metadata']['title'],'artifact':ar,'boundary_basis':region['boundary_basis'],'review_status':'pending'})
        if args.limit and len(items)>=args.limit:break
    save_json(WORK/'region-review.json',items);print(json.dumps({'proposed_regions':len(items)},ensure_ascii=False))

if __name__=='__main__':main()
