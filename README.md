# ECReporting

一款前后端分离的报表与数据填报 Web 应用：
- 后端：Django + DRF（JWT 鉴权）
- 前端：Vue3 + Vite + Element Plus
- 应用元数据：PostgreSQL（兼容 15-18）
- 数据源实例：PostgreSQL / MySQL

## 功能概览

- 人员权限管理：管理员/普通用户，基于用户组授权
- 模块分级：
  - 报表模块（一级）：集合（相当于二级模块）→ 查询/看板
  - 数据填报模块（一级）：上传模块（相当于二级模块）
- 数据报表：
  - SQL 查询（仅允许 SELECT/WITH）
  - 查询可配置可视化（ECharts）
  - 看板可拼接多个查询组件（拖拽/缩放）
  - SQL 隐藏：隐藏后仅管理员/集合创建者/查询创建者可查看与编辑 SQL
- 数据填报：
  - 下载表模板（CSV/XLSX，表头两行：英文名/中文名）
  - 上传 CSV/XLSX 入库

## 部署

- 部署手册：`docs/deploy.md`
- 数据库初始化：`docs/db-init.md`
