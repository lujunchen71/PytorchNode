# 将项目备份到 GitHub 的完整步骤指南

本文档指导您如何在 GitHub 上创建远程仓库，并将本地项目推送到该仓库。

## 前提条件

- 已安装 Git（本任务已完成）
- 拥有 GitHub 账号（您已拥有）
- 能够访问 GitHub 网站（https://github.com）

## 步骤概览

1. 在 GitHub 上创建新仓库
2. 生成个人访问令牌（用于身份验证）
3. 将本地 Git 仓库与远程仓库关联
4. 推送代码到远程仓库

## 详细步骤

### 1. 在 GitHub 上创建新仓库

1. 登录 GitHub（https://github.com）
2. 点击右上角 “+” 图标，选择 “New repository”
3. 填写仓库信息：
   - **Repository name**：输入仓库名称，例如 `PytorchNode`
   - **Description**（可选）：填写项目描述
   - 选择 **Public**（公开）或 **Private**（私有）
   - **Initialize this repository with a README**：**不要勾选**（因为本地已有 README.md）
   - **Add .gitignore**：选择 **None**（本地已有 .gitignore）
   - **Choose a license**：选择 **None**（本地已有 LICENSE 文件）
4. 点击 “Create repository” 按钮

创建成功后，您将看到一个页面，显示远程仓库的 URL（HTTPS 或 SSH）。请复制 **HTTPS** 格式的 URL，例如：
```
https://github.com/您的用户名/PytorchNode.git
```

### 2. 生成个人访问令牌（Token）

因为 GitHub 已禁用密码推送，您需要使用 Token 进行身份验证。

1. 点击 GitHub 右上角头像 → **Settings**
2. 左侧菜单最下方找到 **Developer settings**
3. 选择 **Personal access tokens** → **Tokens (classic)**
4. 点击 **Generate new token** → **Generate new token (classic)**
5. 填写 Note（例如 “PytorchNode backup”）
6. 选择有效期（建议选 “No expiration” 或较长期限）
7. 勾选权限范围：至少需要 **repo**（全部仓库权限）
8. 点击 **Generate token**
9. **立即复制生成的 Token**（只显示一次，务必保存）

### 3. 将本地仓库与远程仓库关联

在本地项目目录（`d:/PytorchNode`）中执行以下命令（使用 Git Bash、PowerShell 或命令提示符）：

```bash
# 添加远程仓库（将下面的 URL 替换为您复制的真实 URL）
git remote add origin https://github.com/您的用户名/PytorchNode.git

# 验证远程仓库是否添加成功
git remote -v
```

如果之前已添加过远程仓库，可以使用以下命令更新 URL：

```bash
git remote set-url origin https://github.com/您的用户名/PytorchNode.git
```

### 4. 推送代码到远程仓库

执行推送命令，Git 会提示输入用户名和密码。**密码处请粘贴刚才复制的 Token**。

```bash
git push -u origin master
```

如果出现身份验证对话框：
- **Username**：输入您的 GitHub 用户名
- **Password**：粘贴 Token（不会显示，直接粘贴后按回车）

推送成功后，终端会显示类似以下信息：
```
Branch 'master' set up to track remote branch 'master' from 'origin'.
```

### 5. 验证推送结果

1. 刷新 GitHub 仓库页面，您应该能看到所有文件已上传。
2. 可以执行 `git log --oneline` 查看提交记录。
3. 后续若本地有新的修改，只需执行以下命令即可推送：

```bash
git add .
git commit -m "提交描述"
git push
```

## 常见问题

### 1. 推送时提示 “remote: Invalid username or password”
- 确保用户名正确
- 确保 Token 具有 repo 权限且未过期
- 如果使用了两步验证，必须使用 Token

### 2. 推送时提示 “remote: Repository not found”
- 检查远程仓库 URL 是否正确
- 确认仓库是否已创建且您有写入权限

### 3. 想更换远程仓库地址
```bash
git remote set-url origin 新的仓库URL
```

### 4. 想查看当前远程仓库配置
```bash
git remote -v
```

## 本地备份包的使用

除了远程备份，您还可以使用之前生成的 `backup.bundle` 文件进行本地备份：

- **将备份包复制到安全位置**（如 U 盘、云盘、另一台电脑）
- **从备份包恢复项目**：
  ```bash
  git clone backup.bundle 新目录名
  ```

## 后续建议

- 定期执行 `git add .`、`git commit -m "描述"`、`git push` 以保持远程仓库与本地同步。
- 重要修改前建议创建分支（`git branch 新分支名`）进行开发。

---

如果您在操作过程中遇到任何问题，请将错误信息复制下来，以便进一步排查。