#!/usr/bin/env python3
import argparse, datetime
from pathlib import Path
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
FONT='/Users/fanlili/Library/Fonts/Alibaba-PuHuiTi-Bold.otf'
DAY='一二三四五六日'
SPECS={
 'high':[((2615,415,2870,515),77,(233,92,0)),((2550,535,2922,613),43,(233,92,0))],
 'mass':[((2500,165,2840,275),82,(237,100,43)),((2535,857,2930,920),43,(237,100,43))]
}

def edit(source,out,kind,city,date):
    image=cv2.imread(str(source))
    if image is None: raise RuntimeError(f'Cannot read {source}')
    for idx,((x0,y0,x1,y1),size,color) in enumerate(SPECS[kind]):
        B,G,R=cv2.split(image)
        orange=(R>175)&(G>55)&(G<185)&(B<135)&(R>G*1.30)
        mask=np.zeros(image.shape[:2],np.uint8)
        mask[y0:y1,x0:x1]=orange[y0:y1,x0:x1].astype(np.uint8)*255
        mask=cv2.dilate(mask,np.ones((5,5),np.uint8),iterations=1)
        image=cv2.inpaint(image,mask,5,cv2.INPAINT_TELEA)
        rgb=Image.fromarray(cv2.cvtColor(image,cv2.COLOR_BGR2RGB))
        label=city+'站' if idx==0 else f'{date.month}月{date.day}日（周{DAY[date.weekday()]}）'
        center=((x0+x1)/2 if idx==0 else 2745,(y0+y1)/2)
        ImageDraw.Draw(rgb).text(center,label,font=ImageFont.truetype(FONT,size),fill=color,anchor='mm')
        image=cv2.cvtColor(np.array(rgb),cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(out),image)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--city',required=True)
    p.add_argument('--date',required=True,help='YYYY-MM-DD')
    p.add_argument('--time',default='',help='For checking only; not printed')
    p.add_argument('--out',required=True)
    args=p.parse_args()
    date=datetime.date.fromisoformat(args.date)
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    for kind,name in [('high','高净值场'),('mass','大众场')]:
        for page in ['cover','body']:
            source=ROOT/'assets'/f'{kind}_style2_{page}.png'
            target=out/f'{args.city}_{name}_{page}_{date.isoformat()}.png'
            edit(source,target,kind,args.city,date)
            print(target)
if __name__=='__main__': main()
