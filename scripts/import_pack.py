"""Restore the uploaded resource pack and build website asset indexes."""
from pathlib import Path,PurePosixPath
from io import BytesIO
from zipfile import ZipFile
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
def run():
 manifest=json.loads((ROOT/'.import/manifest.json').read_text())
 data=b''.join((ROOT/path).read_bytes() for path in manifest['parts'])
 assert len(data)==manifest['bytes'],'Archive size mismatch'
 assert hashlib.sha256(data).hexdigest()==manifest['sha256'],'Archive checksum mismatch'
 with ZipFile(BytesIO(data)) as z:
  files=[i for i in z.infolist() if not i.is_dir()]
  assert len(files)==manifest['files'],'Archive file count mismatch'
  assert len({i.filename for i in files})==len(files),'Duplicate archive paths'
  for info in files:
   path=PurePosixPath(info.filename)
   assert not path.is_absolute() and '..' not in path.parts
   assert path.parts[0] in ['assets','LICENSE','pack.mcmeta','pack.png'],info.filename
   assert ((info.external_attr>>16)&0o170000)!=0o120000,'Symlink not supported'
  for info in files:
   target=ROOT/info.filename;target.parent.mkdir(parents=True,exist_ok=True)
   target.write_bytes(z.read(info))
 from build_web_indexes import build
 build(manifest)
 shutil.rmtree(ROOT/'.import')
 print(f"Imported and verified {len(files)} resource-pack files")
if __name__=='__main__':run()
