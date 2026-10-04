#!/bin/zsh
# usage: cap.sh out.png x y z pitch yaw
export UE_MCP_URL=http://127.0.0.1:8771/mcp
python3 /Users/midir/sm2-n1/city/tools/ue/mcp.py call EditorToolset.EditorAppToolset CaptureViewport "{\"captureTransform\":{\"location\":{\"x\":$2,\"y\":$3,\"z\":$4},\"rotation\":{\"pitch\":$5,\"yaw\":$6,\"roll\":0},\"scale\":{\"x\":1,\"y\":1,\"z\":1}},\"annotations\":{\"gridSpacing\":0,\"gridExtent\":0,\"gridHeight\":0,\"maxLabelDistance\":0,\"classFilter\":{\"refPath\":\"/Script/Engine.Actor\"},\"maxLabels\":0},\"bShowUI\":false}" | python3 -c "import json,base64,sys;d=json.load(sys.stdin)['returnValue'];open('$1','wb').write(base64.b64decode(d['image']['data']))"
