# ADR-0001: LLM provider 选 GLM-4-flash + multi-provider 适配

## 背景

Phase 1 部署在 GitHub Actions, 无法用公司内部 LLM Gateway。需要选一个公网可访问、便宜或免费、质量够用的 LLM。

任务画像:
- 分类 (`classify`): 输入标题+摘要 200 字, 输出 1 个赛道枚举 + 1 个厂商串
- 提炼 (`insight`): 输入摘要 500 字, 输出 1 个 headline + 3-5 条 fact + 1 段产业意义
- 突发判定 (`urgent`): 二选一, 输出 yes/no + 一句话原因
- 周报总结 (`weekly`): 输入 N 条 headline, 输出 1500 字 markdown 总结

预估调用量: 5000-7000 次/月 (daily ~50 条, weekly 1 次, alerts 偶发)。

## 决策

默认用智谱 GLM-4-flash (免费), 通过 OpenAI 兼容协议接入。代码侧通过三个环境变量切换 provider:
- `LLM_API_KEY`
- `LLM_BASE_URL` (例: `https://open.bigmodel.cn/api/paas/v4/`)
- `LLM_MODEL` (例: `glm-4-flash`)

不锁死 SDK, 不写 provider-specific 代码。

## 数据依据

- 复用 `news_collector` 项目的同一栈, 在 GLM-4-flash 上跑了 2 个月, 200-500 字摘要质量满足
- 智谱免费额度对该调用量绰绰有余
- OpenAI 兼容协议 = 切 DeepSeek / Together / 其它兼容厂商只改 Secrets, 不改代码
- GitHub Actions 走公网, 国内 LLM 端点访问稳定

## 权衡

**好处**:
- 0 成本起步
- 切其它 provider 只改 Secrets, 不改代码
- 多 provider 适配天然分散单点风险

**代价**:
- GLM-4-flash 长摘要质量略弱于 Claude / GPT-4
- Phase 2 周报质量不够时升级到 glm-4-plus 或切 DeepSeek

## Phase 2 触发条件

如果连续 2 周用户反馈周报"没看头"或"过于流水账", 升级 model 到 glm-4-plus 试一周对比。
