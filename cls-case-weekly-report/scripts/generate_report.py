#!/usr/bin/env python3
"""
Redmine 项目周报脚本 - Ruijie-CS8862A
每周五运行，生成项目问题周报
"""
import csv
import io
import subprocess
import re
import urllib.parse
from datetime import datetime, timedelta
from collections import Counter

REDMINE_URL = "https://support.clourneysemi.com/redmine"
PROJECT = "rujie-cs8862a"
USERNAME = "<YOUR_USERNAME>"
PASSWORD = "<YOUR_PASSWORD>"
COOKIE_FILE = "/tmp/redmine_weekly_cookies"


def login():
    """登录 Redmine 并保存 cookies"""
    result = subprocess.run([
        'curl', '-s', '-c', COOKIE_FILE, '-L',
        '-o', '/tmp/redmine_login.html',
        f'{REDMINE_URL}/login',
        '--max-time', '30'
    ], capture_output=True, text=True)

    with open('/tmp/redmine_login.html') as f:
        html = f.read()

    m = re.search(r'name="authenticity_token" value="([^"]*)"', html)
    if not m:
        print("ERROR: 无法获取 CSRF token")
        return False
    token = m.group(1)

    data = f"username={urllib.parse.quote(USERNAME)}&password={urllib.parse.quote(PASSWORD)}&authenticity_token={urllib.parse.quote(token)}"
    result = subprocess.run([
        'curl', '-s', '-c', COOKIE_FILE, '-b', COOKIE_FILE,
        '-L', '-o', '/tmp/redmine_post_login.html', '-w', '%{http_code}',
        '-H', 'Content-Type: application/x-www-form-urlencoded',
        '-d', data,
        f'{REDMINE_URL}/login',
        '--max-time', '30'
    ], capture_output=True, text=True)

    if '我的工作台' in open('/tmp/redmine_post_login.html').read():
        return True
    print(f"ERROR: 登录失败, HTTP {result.stdout}")
    return False


def fetch_issues():
    """下载 CSV 格式的所有问题"""
    url = (f"{REDMINE_URL}/projects/{PROJECT}/issues.csv"
           f"?set_filter=1&status_id=*&sort=id%3Adesc"
           f"&c%5B%5D=project&c%5B%5D=tracker&c%5B%5D=status"
           f"&c%5B%5D=priority&c%5B%5D=category&c%5B%5D=created_on"
           f"&c%5B%5D=closed_on&c%5B%5D=updated_on&c%5B%5D=cf_3"
           f"&c%5B%5D=fixed_version&c%5B%5D=done_ratio"
           f"&c%5B%5D=assigned_to&c%5B%5D=subject&c%5B%5D=tags")

    result = subprocess.run([
        'curl', '-s', '-b', COOKIE_FILE, '-L',
        '-o', '/tmp/redmine_issues_weekly.csv',
        url, '--max-time', '30'
    ], capture_output=True, text=True)

    with open('/tmp/redmine_issues_weekly.csv', 'rb') as f:
        raw = f.read()
    return raw.decode('gbk', errors='replace')


def parse_date(s):
    """解析日期字符串"""
    if not s or not s.strip():
        return None
    for fmt in ['%Y-%m-%d %H:%M', '%Y-%m-%d']:
        try:
            return datetime.strptime(s.strip(), fmt)
        except ValueError:
            continue
    return None


def analyze():
    """分析数据并生成报告"""
    text = fetch_issues()
    reader = csv.DictReader(io.StringIO(text))
    issues = list(reader)

    today = datetime.now()
    today = today.replace(hour=23, minute=59, second=59)
    week_start = today - timedelta(days=today.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0)

    parsed = []
    for i in issues:
        rec = {
            'id': int(i['#']),
            'status': i['状态'],
            'priority': i['优先级'],
            'tracker': i['跟踪'],
            'assigned_to': i['指派给'],
            'subject': i['主题'],
            'category': i['类别'],
            'version': i['问题版本号'],
        }
        rec['created_dt'] = parse_date(i['创建于'])
        rec['closed_dt'] = parse_date(i['结束日期'])
        rec['updated_dt'] = parse_date(i['更新于'])
        parsed.append(rec)

    # ── 本周解决 ──
    resolved_ids = set()
    resolved_week = []
    for p in parsed:
        if p['status'] in ('已解决', '已关闭', '已拒绝'):
            dt = p['closed_dt'] or p['updated_dt']
            if dt and week_start <= dt <= today:
                if p['id'] not in resolved_ids:
                    resolved_ids.add(p['id'])
                    resolved_week.append(p)

    # ── 当前未决 ──
    open_statuses = ['新建', '进行中', '反馈']
    open_issues = [p for p in parsed if p['status'] in open_statuses]

    # ── 全部状态分布 ──
    total = len(parsed)
    status_count = Counter(p['status'] for p in parsed)

    # ── 未决分析 ──
    assignee_open = Counter(p['assigned_to'] for p in open_issues if p['assigned_to'])
    priority_open = Counter(p['priority'] for p in open_issues)

    # 超期问题（超过30天未关闭）
    stale = []
    for p in open_issues:
        if p['created_dt']:
            days = (today - p['created_dt']).days
            if days > 30:
                stale.append((p, days))
    stale.sort(key=lambda x: -x[1])

    # 高优先级未决
    high_priority_open = [p for p in open_issues if p['priority'] in ('立刻', '紧急', '高')]

    # ── 近4周趋势 ──
    weekly_closed = []
    for w in range(4):
        ws = week_start - timedelta(weeks=w)
        we = ws + timedelta(days=6, hours=23, minutes=59)
        count = 0
        seen = set()
        for p in parsed:
            if p['status'] in ('已解决', '已关闭', '已拒绝'):
                dt = p['closed_dt'] or p['updated_dt']
                if dt and ws <= dt <= we and p['id'] not in seen:
                    seen.add(p['id'])
                    count += 1
        weekly_closed.append((ws, we, count))

    # ── 生成报告 ──
    lines = []
    lines.append(f"## Ruijie-CS8862A 项目周报")
    lines.append(f"**报告周期**: {week_start.strftime('%Y-%m-%d')} ~ {today.strftime('%Y-%m-%d')}")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    # 1. 概要
    lines.append("### 📊 概要")
    lines.append(f"- 项目问题总数: **{total}**")
    lines.append(f"- 本周解决/关闭: **{len(resolved_week)}** 个")
    lines.append(f"- 当前未决问题: **{len(open_issues)}** 个")
    lines.append(f"- 累计已关闭: **{status_count.get('已关闭', 0)}** 个")
    lines.append(f"- 累计已解决: **{status_count.get('已解决', 0)}** 个")
    lines.append("")

    # 2. 本周解决详情
    lines.append("### ✅ 本周解决问题")
    if resolved_week:
        lines.append("")
        lines.append("```")
        lines.append(f"{'ID':>6} | {'优先级':6s} | {'处理人':14s} | 问题描述")
        lines.append("-" * 80)
        for p in resolved_week:
            subj = p['subject'][:50]
            lines.append(f"#{p['id']:>5} | {p['priority']:6s} | {p['assigned_to']:14s} | {subj}")
        lines.append("```")
    else:
        lines.append("本周无解决问题。")
    lines.append("")

    # 3. 当前未决问题
    lines.append("### 🔴 当前未决问题")
    lines.append("")
    lines.append("```")
    lines.append(f"{'ID':>6} | {'状态':8s} | {'优先级':6s} | {'天数':>4} | {'处理人':14s} | 问题描述")
    lines.append("-" * 100)
    for p in open_issues:
        days = (today - p['created_dt']).days if p['created_dt'] else '?'
        subj = p['subject'][:55]
        lines.append(f"#{p['id']:>5} | {p['status']:8s} | {p['priority']:6s} | {str(days):>4} | {p['assigned_to']:14s} | {subj}")
    lines.append("```")
    lines.append("")

    # 4. 未决问题分布
    lines.append("### 👥 未决问题分布")
    lines.append("")
    lines.append("**按处理人**:")
    lines.append("```")
    for name, cnt in assignee_open.most_common():
        bar = "█" * cnt
        lines.append(f"  {name:14s} {bar} {cnt}")
    lines.append("```")
    lines.append("")
    lines.append("**按优先级**:")
    lines.append("```")
    for p, cnt in priority_open.most_common():
        bar = "█" * cnt
        lines.append(f"  {p:6s} {bar} {cnt}")
    lines.append("```")
    lines.append("")

    # 5. 超期问题预警
    if stale:
        lines.append("### ⚠️ 超期未决 (>30天)")
        lines.append("")
        lines.append("```")
        lines.append(f"{'ID':>6} | {'天数':>4} | {'优先级':6s} | {'处理人':14s} | 问题描述")
        lines.append("-" * 95)
        for p, days in stale:
            subj = p['subject'][:50]
            lines.append(f"#{p['id']:>5} | {days:>4} | {p['priority']:6s} | {p['assigned_to']:14s} | {subj}")
        lines.append("```")
        lines.append("")

    # 6. 高优先级未决
    if high_priority_open:
        lines.append("### 🔥 高优先级未决")
        lines.append("")
        lines.append("```")
        lines.append(f"{'ID':>6} | {'天数':>4} | {'优先级':6s} | {'处理人':14s} | 问题描述")
        lines.append("-" * 95)
        for p in high_priority_open:
            days = (today - p['created_dt']).days if p['created_dt'] else '?'
            subj = p['subject'][:50]
            lines.append(f"#{p['id']:>5} | {str(days):>4} | {p['priority']:6s} | {p['assigned_to']:14s} | {subj}")
        lines.append("```")
        lines.append("")

    # 7. 解决趋势
    lines.append("### 📈 近4周解决趋势")
    lines.append("")
    lines.append("```")
    for ws, we, cnt in weekly_closed:
        bar = "█" * min(cnt, 20)
        lines.append(f"  {ws.strftime('%m/%d')}-{we.strftime('%m/%d')}: {bar} {cnt}")
    lines.append("```")
    lines.append("")

    # 8. 风险分析
    lines.append("### 📋 概要分析")
    lines.append("")
    avg_weekly = sum(c for _, _, c in weekly_closed) / max(1, len([c for _, _, c in weekly_closed if c > 0]))
    lines.append(f"- **解决速度**: 近4周平均每周解决 {avg_weekly:.1f} 个问题")
    if len(open_issues) > 0 and avg_weekly > 0:
        weeks_to_clear = len(open_issues) / avg_weekly
        lines.append(f"- **清空预估**: 按当前速率需约 {weeks_to_clear:.1f} 周清空未决问题")

    total_assignees = len(assignee_open)
    lines.append(f"- **投入资源**: 当前 {total_assignees} 人处理未决问题")
    max_load = max(assignee_open.values()) if assignee_open else 0
    max_person = assignee_open.most_common(1)[0][0] if assignee_open else ''
    if max_load >= 5:
        lines.append(f"- **负载不均**: {max_person} 承担了 {max_load} 个未决问题({max_load/len(open_issues)*100:.0f}%)，建议分流")

    stale_high = [p for p, d in stale if p['priority'] in ('立刻', '紧急', '高')]
    if stale_high:
        lines.append(f"- **⚠️ 高风险**: {len(stale_high)} 个高优先级问题超期超过30天")

    resolved_total = status_count.get('已解决', 0) + status_count.get('已关闭', 0) + status_count.get('已拒绝', 0)
    lines.append(f"- **项目整体**: 共 {total} 个问题，已解决 {resolved_total} 个 ({resolved_total/total*100:.1f}%)，未决 {len(open_issues)} 个")

    if stale:
        lines.append(f"- **超期问题**: {len(stale)} 个问题超过30天未关闭，需重点关注")

    return "\n".join(lines)


if __name__ == "__main__":
    if not login():
        exit(1)
    report = analyze()
    print(report)
