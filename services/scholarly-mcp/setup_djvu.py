"""Build pinned upstream DjVu decoding tools with the installed Windows MSVC.

No installer, registry edit, global PATH change, or Python dependency is needed.
The generated tools and the upstream license stay in this service's ignored data.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from waits import LOCAL_TOOL_S

SERVICE=Path(__file__).resolve().parent
UPSTREAM='https://git.code.sf.net/p/djvu/djvulibre-git'
COMMIT='4847901fa2d81cdf8db89cc22f63ae5de85f963a'
TOOLS=('djvutxt','djvused','ddjvu')
LICENSE='GPL-2.0-or-later'


def run(args,*,env=None,log=None):
    result=subprocess.run(list(map(str,args)),cwd=SERVICE,capture_output=True,env=env,timeout=LOCAL_TOOL_S,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if log:log.write_bytes(result.stdout+result.stderr)
    if result.returncode:
        raise RuntimeError(f'{Path(str(args[0])).name} failed with exit {result.returncode}; see {log or "setup output"}')
    return result.stdout.decode('utf-8','replace').strip()


def main():
    if os.name!='nt':raise RuntimeError('This build recipe targets the selected Windows host')
    compiler_name=shutil.which('cl.exe')
    if not compiler_name:raise RuntimeError('The installed MSVC compiler must be available to setup')
    compiler=Path(compiler_name);msvc=compiler.parents[3]
    kits=Path(os.environ.get('ProgramFiles(x86)',r'C:\Program Files (x86)'))/'Windows Kits/10'
    versions=[path for path in (kits/'Include').iterdir() if (path/'um/windows.h').is_file()]
    sdk=max(versions,key=lambda path:tuple(map(int,path.name.split('.'))))
    env=dict(os.environ)
    env['INCLUDE']=';'.join(map(str,[msvc/'include',*[sdk/name for name in ('ucrt','shared','um','winrt')]]))
    env['LIB']=';'.join(map(str,[msvc/'lib/x64',kits/'Lib'/sdk.name/'ucrt/x64',kits/'Lib'/sdk.name/'um/x64']))
    root=SERVICE/'data/tools/djvulibre';root.mkdir(parents=True,exist_ok=True)
    source=root/'source';build=root/'build';runtime=root/'runtime'
    for folder in (build,runtime):folder.mkdir(exist_ok=True)
    if not source.exists():run(['git','clone','--depth','1',UPSTREAM,source],log=root/'clone.log')
    if run(['git','-C',source,'status','--porcelain']):raise RuntimeError('The dedicated upstream checkout contains local changes')
    if run(['git','-C',source,'rev-parse','HEAD'])!=COMMIT:
        run(['git','-C',source,'fetch','--depth','1',UPSTREAM,COMMIT],log=root/'fetch.log')
        run(['git','-C',source,'checkout','--detach',COMMIT],log=root/'checkout.log')
    filenames=run(['git','-C',source,'ls-files','libdjvu/*.cpp']).splitlines()
    files=[source/name for name in filenames]
    flags=['/nologo','/std:c++14','/EHsc','/O2','/MT','/DHAVE_NAMESPACES','/DDJVUAPI=','/DDDJVUAPI=',
        '/DMINILISPAPI=','/DNDEBUG','/D_CRT_SECURE_NO_WARNINGS','/wd4996','/wd4244','/wd4267',
        '/wd4302','/wd4311','/wd4312','/MP4','/I'+str(source),'/I'+str(source/'libdjvu')]
    run([compiler,*flags,'/c',*files,'/Fo'+str(build)+'\\'],env=env,log=root/'compile.log')
    objects=[build/(path.stem+'.obj') for path in files]
    run([compiler.with_name('lib.exe'),'/nologo','/OUT:'+str(build/'djvu.lib'),*objects],env=env,log=root/'library.log')
    manifest={'upstream':UPSTREAM,'commit':COMMIT,'license':LICENSE,'tools':{},
        'build':'MSVC static runtime; DjVu text and PPM rendering; TIFF/PDF encoding not included'}
    for tool in TOOLS:
        executable=runtime/(tool+'.exe')
        run([compiler,*flags,source/'tools'/(tool+'.cpp'),build/'djvu.lib','/Fo'+str(build/(tool+'.obj')),
            '/Fe'+str(executable),'/link','user32.lib','advapi32.lib','gdi32.lib'],env=env,log=root/(tool+'-build.log'))
        data=executable.read_bytes()
        manifest['tools'][executable.name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
    shutil.copyfile(source/'COPYING',runtime/'COPYING')
    (runtime/'provenance.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'completed':True,'commit':COMMIT,'tools':len(TOOLS),'bytes':sum(value['bytes'] for value in manifest['tools'].values())}))


if __name__=='__main__':main()
