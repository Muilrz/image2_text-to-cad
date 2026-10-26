# text-to-cad Visual

基于 **earthtojake/text-to-cad 0.7.24** 的独立实验性衍生插件，在图像重建之前增加 Visual Inspector，并把标准 CAD Visual Spec 交回原主会话。

本项目由本地改造版本整理而来，不是上游官方发布，也不代表上游对这些改动的认可。上游项目：https://github.com/earthtojake/text-to-cad 。

## 改进与流程

```text
原始用户需求 + 原始参考图片
          │
          ├── 独立、只读 Visual Inspector 子会话
          │                    ↓
          │            标准 CAD Visual Spec
          │                    │
          └────────────────────┘
                               ↓
           原 Codex 主会话：需求 + 原图 + Spec
                               ↓
              原有 CAD 建模、验证与导出流程
                               ↓
                              CAD
```

- 预检重点：主表面、表面过渡、轮廓曲线、截面变化，以及容易遗漏的浅凸/浅凹、渐变和扭转。
- 以 P0/P1/UNKNOWN 分组，保留置信度、视图、视觉依据和建模影响。
- 主会话保留原始需求和原图；Spec 是补充证据，P0 不自动高于原图。
- JSON 经本地校验后生成 Markdown，记录图片与需求哈希、执行模式和 run ID。
- 独立子会话失败时允许明确标记的主会话降级；不会宣称执行过隔离分析。
- 继承上游 CAD、工程图、DFM/DfAM、零件查找、切片及机器人描述等 skills。CAD 运行时继续固定为 cadgen 0.7.24。

新增文件集中在 `plugins/text-to-cad-visual/skills/image-cad-preflight/`，建模入口改动在副本的 `skills/cad/` 中。版本 0.7.24 表示所基于的上游版本；本实验修订号为 1。

## 安装

当前安装说明面向 Codex。需要支持 `plugin` 子命令的 Codex CLI、可用的 CLI 登录状态、Python 3.10 或更新版本，以及能运行继承 CAD 工作流的 uv/uvx。Inspector helper 只依赖 Python 标准库；CAD 运行时按继承的插件配置获取。

先在终端检查环境：

```powershell
python --version
codex --version
codex plugin --help
codex login status
uvx --version
python scripts/doctor.py
```

`doctor.py` 只检查命令和所需参数是否可用，不启动模型推理、不下载 CAD 引擎。CLI 未登录时先执行 `codex login`。若 `python` 不存在，Windows 可使用已安装的 `py -3`，macOS/Linux 可使用 `python3`；把后续命令中的 `python` 换成相应命令。首次 CAD 启动需要联网下载固定版本的运行时，图片分析也需要可用的模型服务。仅解压 ZIP 并不会安装这些依赖。

本机核对的 CLI 是 `0.164.0-alpha.11.1`，这不是宣称的最低版本。你的 CLI 必须支持 `plugin marketplace add`，以及 `exec --image --output-schema --output-last-message --ephemeral --sandbox --skip-git-repo-check --cd`。可先运行上述检查，遇到缺失参数时更新 CLI 后重试。

克隆仓库后，从仓库根目录注册本地市场：

```powershell
codex plugin marketplace add . --json
codex plugin add text-to-cad-visual@ming-cad-lab --json
```

也可以直接使用 GitHub 仓库地址注册市场：

```powershell
codex plugin marketplace add Muilrz/image2_text-to-cad --json
codex plugin add text-to-cad-visual@ming-cad-lab --json
```

本项目仓库：https://github.com/Muilrz/image2_text-to-cad 。已注册同名市场时，先查看现有来源，避免把开发目录和远程来源混淆。

新会话中选择 **text-to-cad Visual (experimental)**，上传参考图并描述建模需求。第一次使用可明确说明：

> 请先启动独立 Visual Inspector 生成标准 CAD Spec，再由当前主会话结合原始需求、原图和 Spec 继续建模，并说明预检执行模式。

原版插件 ID 是 `text-to-cad@earthtojake`；本项目插件 ID 是 `text-to-cad-visual@ming-cad-lab`，MCP 服务键为 `cad_visual`。可保留原版分别进行对比；每次明确选择所用插件。

## 输出与边界

输出保存在当前 CAD 项目的 `.cad_context/`，不写入插件目录：

```text
request.txt       原始需求
visual_spec.md    主会话读取的 Spec
visual_spec.json  来源记录与 inspection 对象
```

- `isolated-child`：由独立 `codex exec` 子会话完成。
- `main-session`：由主会话检查，未宣称有隔离分析。

临时目录减少项目上下文干扰，不保证移除全局配置。子会话默认使用 Codex CLI 配置，不能据此保证与主会话 UI 的模型选择完全相同。单图无法确定的隐藏几何、精确尺寸和半径仍然属于未知或明确标注的假设。

预检路由通过 skill 指令实现；不是应用层强制钩子。未使用图像重建时不要求额外预检。

## 独立 GUI

`plugins/text-to-cad-visual/gui/` 保存基于 cadgen 0.7.24 的独立 GUI 文件。
Codex 使用实验版配置中的插件相对工作目录和 `CADGEN_MCP_APP_DIR=gui`
加载它，原版插件和共享 cadgen 缓存保持不变。界面作者显示追加 `, Ming Liu`，
GitHub 菜单与反馈入口指向本项目；引擎版本信息不变。

更改仅在同步安装缓存并重新启动 MCP 服务后生效。仅修改工作目录不会让当前已打开的界面热更新。
重建命令与来源哈希见 `gui/README.md`。当前为 Codex 集成界面配置，独立浏览器 Viewer 与其他宿主的界面未修改。

## 验证与对比

```powershell
python -m unittest discover -s tests -v
python scripts/check_fork.py
```

程序测试覆盖来源追踪、输出校验、多视图、输入保护、降级标记、失败与超时。子会话成功路径使用模拟结果，不能作为识图质量基准。原维护者报告在本地实验中获得了较好效果，目前未提供可公开复现的量化数据集。

进行 A/B 对比时，新开独立会话，固定原始需求、参考图片、模型设置和输出要求，分别选择原版与实验版。不要把实验版 Spec 带入原版会话。记录模板见 `AB_TEST_TEMPLATE.md`。

## 开发与发布

当前仓库根目录是唯一维护的源码。其 Git 根目录应当就是本目录（`text-to-cad-visual-ab`），不能是包含其他项目的父目录。直接在这里用 Git 管理和推送，不需要维护另一份发布源码。`dist/` 中的 ZIP 或快照只是可选产物，不作为后续修改来源。修改插件后需要重新安装，Codex 安装缓存不会自动同步。

GitHub Actions 会在 Windows 和 Linux、Python 3.10 和 3.12 上运行程序测试及来源检查；CI 不运行需要个人登录的真实模型推理或完整 CAD 引擎。首次推送后需查看这些检查的实际结果。

本机验证记录和临时文件由 `.gitignore` 排除。运行 `python scripts/check_fork.py` 可检查衍生范围；存在本机 baseline 时会额外核验原版文件。

## 目录

```text
.agents/plugins/marketplace.json
plugins/text-to-cad-visual/
  .codex-plugin/plugin.json
  codex.mcp.json
  skills/
  gui/             实验版独立界面与来源记录
  LICENSE
  NOTICE.md
  UPSTREAM_README.md
tests/
LICENSE
NOTICE.md
UPSTREAM.json
PUBLISHING.md
```

当前优先验证 Codex 安装路径；继承的其他宿主配置不代表已完成相应客户端的安装实测。

## 来源与许可

原版许可证保留在根目录及插件目录的 `LICENSE` 中，包含 **Copyright (c) 2026 Thompson Labs LLC**。本项目的新增代码和文档沿用 MIT 条款。上游作者与项目归属见 `NOTICE.md`，来源版本及原始文件哈希见 `UPSTREAM.json`，修改范围见 `CHANGELOG.md`。

插件清单中的 `author.name` 为 `Ming Liu`，Codex 开发者展示为 `earthtojake, Ming Liu`。CAD GUI 保留原作者并追加 `, Ming Liu`，GitHub 和反馈入口指向本项目。署名不替代上游版权声明。仓库包含独立 GUI 页面及其许可证说明；cadgen Python 引擎、build123d、Open CASCADE 等仍作为外部运行时依赖获取。
