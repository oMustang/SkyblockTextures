"""Generate stable indexes without modifying the original resource-pack files."""
from pathlib import Path
import json,struct,hashlib
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text())
def output(name,data):
 p=ROOT/'web'/name;p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
def texture_path(ref):
 namespace,path=ref.split(':',1) if ':' in ref else ('minecraft',ref)
 return f'assets/{namespace}/textures/{path}.png'
def model_path(ref):
 namespace,path=ref.split(':',1) if ':' in ref else ('minecraft',ref)
 return ROOT/f'assets/{namespace}/models/{path}.json'
def get_gui_model(model):
 if isinstance(model,str):return model
 if not isinstance(model,dict):return None
 kind=model.get('type','')
 if kind in ('minecraft:model','model'):return model.get('model')
 if kind=='minecraft:select' and model.get('property')=='minecraft:display_context':
  for c in model.get('cases',[]):
   when=c.get('when',[]);when=[when] if isinstance(when,str) else when
   if 'gui' in when:return get_gui_model(c.get('model',{}))
  return get_gui_model(model.get('fallback',{}))
 return None
def model_textures(ref,seen=None):
 seen=set() if seen is None else seen
 if ref in seen:return {}
 seen.add(ref);p=model_path(ref)
 if not p.exists():return {}
 model=load(p);textures=model_textures(model['parent'],seen) if model.get('parent') else {}
 textures.update(model.get('textures',{}));return textures
def resolve_texture(ref,textures):
 seen=set()
 while ref and ref.startswith('#'):
  if ref in seen:return None
  seen.add(ref);ref=textures.get(ref[1:])
 if ref:
  path=texture_path(ref)
  if (ROOT/path).is_file():return path
 return None
def build(source=None):
 previous=ROOT/'web/pack-info.json'
 if source is None and previous.exists():source=load(previous).get('source',{})
 icons={};models={};item_models={};unresolved=[];collisions=[];animated=0
 for p in sorted((ROOT/'assets/hypixel_skyblock/items').rglob('*.json')):
  definition=load(p);ref=get_gui_model(definition.get('model',{}))
  entry={'definition':str(p.relative_to(ROOT))}
  if ref:
   entry['model']=ref;tex=model_textures(ref)
   layers=[resolve_texture(tex.get(f'layer{n}'),tex) for n in range(8)]
   layers=[x for x in layers if x]
   if layers:
    entry['texture']=layers[0];entry['layers']=layers
    png=(ROOT/layers[0]).read_bytes();width,height=struct.unpack('>II',png[16:24]);entry['width']=width;entry['height']=height
    meta=ROOT/(layers[0]+'.mcmeta')
    if meta.exists():entry['animation']=load(meta).get('animation',{});animated+=1
   else:entry['status']='needs-renderer';unresolved.append(str(p.relative_to(ROOT)))
   models[ref]=entry
  else:entry['status']='dynamic-model';unresolved.append(str(p.relative_to(ROOT)))
  item_models['hypixel_skyblock:'+str(p.relative_to(ROOT/'assets/hypixel_skyblock/items').with_suffix(''))]=entry
  # Basename keys are candidates; item_model from Hypixel's item resource is authoritative.
  candidate=p.stem.upper()
  if candidate in icons:collisions.append(candidate)
  else:icons[candidate]=entry
 output('item-icons.json',{'schema':1,'byItemIdCandidate':icons,'byItemModel':item_models,'byModel':models,'unresolved':unresolved,'collisions':collisions})
 font=load(ROOT/'assets/minecraft/font/default.json');glyphs={};sheets=[]
 for provider in font.get('providers',[]):
  if provider.get('type')!='bitmap':continue
  path='assets/'+provider['file'].replace(':','/textures/',1)
  p=ROOT/path
  if not p.exists():continue
  png=p.read_bytes();width,height=struct.unpack('>II',png[16:24]);rows=provider['chars'];columns=max(map(len,rows));cw=width/columns;ch=height/len(rows)
  sheet={'path':path,'width':width,'height':height,'columns':columns,'rows':len(rows),'cellWidth':cw,'cellHeight':ch,'ascent':provider.get('ascent'),'glyphHeight':provider.get('height')};sheets.append(sheet)
  for y,row in enumerate(rows):
   for x,char in enumerate(row):
    if char=='\0':continue
    glyphs[f'U+{ord(char):04X}']={'character':char,'sheet':path,'x':x*cw,'y':y*ch,'width':cw,'height':ch,'ascent':provider.get('ascent'),'glyphHeight':provider.get('height')}
 output('glyphs.json',{'schema':1,'providers':sheets,'glyphs':glyphs,'baseFontIncluded':False})
 info={'schema':1,'pack':load(ROOT/'pack.mcmeta')['pack'],'originalFiles':4713,'itemDefinitions':len(icons)+len(collisions),'iconsWithTexture':sum('texture' in i for i in icons.values()),'animatedIcons':animated,'unresolvedDefinitions':len(unresolved),'glyphs':len(glyphs),'source':source or {}}
 output('pack-info.json',info)
 print(json.dumps(info,ensure_ascii=False))
if __name__=='__main__':build()
