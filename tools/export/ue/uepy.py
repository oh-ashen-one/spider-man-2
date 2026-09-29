#!/usr/bin/env python3
"""Run a Python file (or -c code) inside THIS worktree's running Unreal Editor via PythonScriptPlugin remote execution.
The editor must be launched with (command-line ini override, shared config untouched):
  [/Script/PythonScriptPlugin.PythonScriptPluginSettings] bRemoteExecution=True,
  RemoteExecutionMulticastGroupEndpoint=239.0.0.71:6771, RemoteExecutionMulticastBindAddress=127.0.0.1
Only the node whose project_root is this worktree's unreal/WebHomage is ever connected to (other agents' editors are
never addressed).  usage: uepy.py file.py [args...]   |   uepy.py -c "code"
"""
import os, sys, time, json
sys.path.insert(0, '/Users/Shared/Epic Games/UE_5.8/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python')
import remote_execution as rx

PROJ = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../../unreal/WebHomage'))

def main():
    cfg = rx.RemoteExecutionConfig()
    cfg.multicast_group_endpoint = ('239.0.0.71', 6771)
    cfg.multicast_bind_address = '127.0.0.1'
    r = rx.RemoteExecution(cfg)
    r.start()
    try:
        node = None
        for _ in range(60):
            for n in r.remote_nodes:
                pr = os.path.realpath(n.get('project_root', '').rstrip('/'))
                if pr == PROJ:
                    node = n; break
            if node: break
            time.sleep(0.25)
        if not node:
            raise SystemExit('my editor node not found (project_root %s); nodes: %s' % (PROJ, [n.get('project_root') for n in r.remote_nodes]))
        r.open_command_connection(node['node_id'])
        if sys.argv[1] == '-c':
            code, mode = sys.argv[2], rx.MODE_EXEC_FILE
        else:
            path = os.path.abspath(sys.argv[1])
            argv = json.dumps([path] + sys.argv[2:])
            code = f"import sys; sys.argv = {argv}; exec(compile(open({path!r}).read(), {path!r}, 'exec'), {{'__name__': '__main__', '__file__': {path!r}}})"
            mode = rx.MODE_EXEC_FILE
        res = r.run_command(code, unattended=True, exec_mode=mode)
        for o in res.get('output', []):
            print(o.get('output', '').rstrip())
        if not res.get('success'):
            print('FAILED:', res.get('result'))
            sys.exit(1)
    finally:
        r.stop()

if __name__ == '__main__':
    main()
