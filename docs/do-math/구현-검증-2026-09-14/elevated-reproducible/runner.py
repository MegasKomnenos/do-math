import json, pathlib, subprocess, sys
request=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
try:
    with open(request["stdout"],"xb") as out, open(request["stderr"],"xb") as err:
        process=subprocess.Popen(request["argv"],stdin=subprocess.DEVNULL,stdout=out,stderr=err,shell=False)
        code=process.wait()
    status={"state":"exited","exit_code":code}
except BaseException as exc:
    status={"state":"program_failed","error_type":type(exc).__name__,"message":str(exc)}
pathlib.Path(request["status"]).write_text(json.dumps(status),encoding="utf-8")
raise SystemExit(0 if status.get("state")=="exited" else 125)
