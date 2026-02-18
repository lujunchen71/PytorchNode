import git
import sys

try:
    repo = git.Repo('.')
    print('当前分支:', repo.active_branch)
    print('远程仓库:')
    for remote in repo.remotes:
        print(f'  {remote.name} -> {remote.url}')
    if len(repo.remotes) == 0:
        print('  无远程仓库')
    print('未跟踪的文件:', repo.untracked_files)
    print('已修改的文件:', [item.a_path for item in repo.index.diff(None)])
except Exception as e:
    print('错误:', e, file=sys.stderr)
    sys.exit(1)