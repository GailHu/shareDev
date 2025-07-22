# 说明
项目中包含Java，js，python等可以分享出来的代码

# 增加AI相关文档

ai目录

# 仓库管理
docker run --rm \
  -e PLUGIN_TARGET_URL="https://github.com/GailHu/shareDev.git" \
  -e PLUGIN_AUTH_TYPE="https" \
  -e PLUGIN_USERNAME="uname" \
  -e PLUGIN_PASSWORD="pwd" \# 注意：需要授权
  -e PLUGIN_BRANCH="main" \
  -v /workspace:/workspace \
  -w /workspace \
  tencentcom/git-sync
> 注意，可能需要强制推送