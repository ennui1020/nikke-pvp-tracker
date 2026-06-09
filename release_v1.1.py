#!/usr/bin/env python3
"""Create GitHub release and upload zip."""
import json, os, re
from urllib.request import Request, urlopen
from urllib.parse import urlparse

# Read token from .git-credentials
git_cred = os.path.expanduser('~/.git-credentials')
with open(git_cred) as f:
    cred = f.read().strip()
token = re.search(r'oauth2:([^@]+)@', cred).group(1)

OWNER = 'ennui1020'
REPO = 'nikke-pvp-tracker'
ZIP_PATH = 'dist/nikke-pvp-tracker-v1.1.zip'
TAG = 'v1.1'

headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json',
}

# Push tag first
print("Pushing tag...")
os.system(f'cd /root/nikke-pvp-tracker && git tag -f {TAG} && git push origin {TAG} -f 2>&1')

# Create release
print("Creating release...")
body = """## v1.1 更新内容

### 角色数据
- 角色总数 **191**（163 SSR + 28 SR）
- 角色名字全量对齐 blablalink（繁体中文 + 全角冒号）
- 新增 9 个角色：產品08/12/23、士兵F.A./E.G./O.W.、iDoll花/太陽/海
- 修正稀有度分类（SSR/SR）

### 头像
- 从 blablalink CDN 批量下载全部 **191 个头像文件**
- 缺头像角色不再显示兜底 SVG，直接用官方头像

### 数据源
- 角色属性（企业/武器/代码/爆裂/职业）基于 blablalink 游戏数据
- 繁简中文搜索正常"""

release_data = {
    'tag_name': TAG,
    'name': f'{TAG} - 全角色数据对齐 blablalink + 191个头像',
    'body': body,
    'draft': False,
    'prerelease': False,
}

req = Request(
    f'https://api.github.com/repos/{OWNER}/{REPO}/releases',
    data=json.dumps(release_data).encode(),
    headers=headers,
    method='POST'
)

resp = urlopen(req)
release = json.loads(resp.read())
release_id = release['id']
print(f'Release created: {release_id}')

# Upload zip
print('Uploading zip...')
zip_size = os.path.getsize(ZIP_PATH)
with open(ZIP_PATH, 'rb') as f:
    upload_url = f'https://uploads.github.com/repos/{OWNER}/{REPO}/releases/{release_id}/assets?name=nikke-pvp-tracker-v1.1.zip'
    upload_headers = {
        'Authorization': f'token {token}',
        'Content-Type': 'application/zip',
        'Content-Length': str(zip_size),
    }
    upload_req = Request(upload_url, data=f, headers=upload_headers, method='POST')
    upload_resp = urlopen(upload_req)
    asset = json.loads(upload_resp.read())
    print(f'Asset uploaded: {asset["name"]} ({asset["size"]} bytes)')

print(f'\nDone! https://github.com/{OWNER}/{REPO}/releases/tag/{TAG}')
