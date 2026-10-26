# 发布到 GitHub

当前工作目录就是源码仓库；直接在这里维护和推送 Git。ZIP 仅用于可选的文件传输或 GitHub Release 附件。不要只把 ZIP 当作仓库中唯一的源码文件上传。

## 许可证与署名

1. 保留根目录和插件目录中的原始 MIT LICENSE，包括 Thompson Labs LLC 的版权行及完整授权、免责文字。
2. README 说明这是衍生实验版，说明改进点、安装方式、行为边界和上游来源。
3. NOTICE 记录上游和本项目改动。NOTICE 是本项目添加的归属说明，并非 MIT 强制规定的文件名。
4. 新增贡献采用 MIT。可以用自己的实际姓名、组织名称或适当署名添加新增贡献的版权行；不要把上游版权行直接替换为自己的名字。
5. 插件 JSON 的 `author.name` 为 `Ming Liu`，开发者展示为 `earthtojake, Ming Liu`，项目地址为 `https://github.com/Muilrz/image2_text-to-cad`。独立 GUI 保留原作者后追加 Ming Liu。保留这些署名及上游许可证，不把上游网站当成本项目支持承诺。

参考：

- MIT 许可证原文：https://opensource.org/license/mit
- GitHub 本地代码上传文档：https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github

## 发布前确认

- Git 应只上传插件源码、测试和公开说明；本地目录仍可能保存被 `.gitignore` 排除的验证记录和临时文件。使用 `git status --short --ignored` 核对，勿使用 `git add -f` 加入本机文件。
- 检查 NOTICE 与元数据中的署名；本项目仓库为 `Muilrz/image2_text-to-cad`。
- 运行 `python -m unittest discover -s tests -v`。
- 如果加入后续测试图片或 CAD 样本，另行确认有公开分享这些资产的权限。

## 创建仓库并推送

当前工作目录已初始化独立 Git 仓库，发布目标为 `https://github.com/Muilrz/image2_text-to-cad.git`。使用公开仓库可让任何人无需授权即可下载。下面的远程添加命令仅在尚未配置 `origin` 时执行；已有远程可用 `git remote -v` 核对。

从**当前工作目录（仓库根目录）**执行，检查 `git rev-parse --show-toplevel` 指向这个新目录：

```powershell
git rev-parse --show-toplevel
git status --short --ignored
git add .
git diff --cached --stat
git commit -m "Add Visual Inspector preflight for text-to-cad"
git remote add origin https://github.com/Muilrz/image2_text-to-cad.git
git push -u origin main
```

如 Git 提示身份信息缺失，使用你真实的 Git 提交身份配置当前仓库。上传前检查暂存清单，不要在包含其他工作的父目录直接执行 `git add .`。

也可以在 GitHub 网页上传源码文件，但要确认 `.agents/`、`.codex-plugin/` 等以点开头的目录没有遗漏。

推送后检查 GitHub Actions 的 Windows/Linux 测试结果，并从 GitHub 地址做一次安装验收，之后再对外宣称远程安装通过。本地测试不能证明远程下载和安装成功。

## 分享给别人

仓库上传完成后，使用者可以运行：

```powershell
codex plugin marketplace add Muilrz/image2_text-to-cad --json
codex plugin add text-to-cad-visual@ming-cad-lab --json
```

若通过 ZIP 分享，则解压后在源码根目录执行 `codex plugin marketplace add . --json`，再安装相同插件 ID。

这会使用仓库内的 marketplace 定义。原维护者的本机开发版已经注册了同名市场；更换本机市场来源之前，应明确选择保留本地开发源还是改为远程源。

创建带版本的 GitHub Release 时，可将源码 ZIP 作为附件。插件自身版本号仍为基线 0.7.24，本实验修订号为 1；开始独立发布前，维护者应确定自己的版本策略，并区分插件版本与 cadgen 运行时版本。
