#!/usr/bin/env python3
"""ai-billing-payment-platform-practice 技能验证脚本。

断言"产出=合规成立"而非"动作已执行"：
- GOOD 样例：含全部合规要素，且无违规 → exit 0
- BAD 样例：命中任一违规模式 → exit 1

退出码契约：0=通过，1=存在错误，2=文件错误。
"""
import re
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_FILE_ERROR = 2


def read_sample(path: str) -> str:
    p = Path(path)
    if not p.is_file():
        print(f"文件不存在: {path}", file=sys.stderr)
        sys.exit(EXIT_FILE_ERROR)
    return p.read_text(encoding="utf-8")


GOOD_REQUIREMENTS = [
    ('MoR|Merchant of Record|代收代付|PSP', '缺少 MoR/PSP 责任边界判断'),
    ('VAT|销售税|GST', '缺少销售税/VAT 核查'),
    ('拒付|chargeback|退款', '缺少拒付与退款机制'),
    ('申报|税号|OSS|IOSS|nexus', '缺少税务申报路径'),
    ('gotchas|坑位|红线', '缺少 gotchas 坑位引用'),
]

BAD_VIOLATIONS = [
    ('(无需|不用|免).{0,6}(缴税|申报|税号|VAT)', '命中违规：免税务申报话术'),
    ('先.{0,4}(收|上线|卖).{0,8}(后|再).{0,4}(补|报|缴)', '命中违规：先收钱后补税'),
    ('(无需|不用|绕开).{0,4}(牌照|许可|license)', '命中违规：绕支付牌照'),
    ('(隐藏|默认勾选|不提示).{0,6}(续费|扣款|订阅)', '命中违规：隐藏自动续费'),
    ('(刷|伪造).{0,4}(拒付|退款|chargeback)', '命中违规：伪造拒付/退款'),
]


def find_violations(text: str) -> list:
    hits = []
    for pattern, msg in BAD_VIOLATIONS:
        if re.search(pattern, text, re.IGNORECASE):
            hits.append(msg)
    return hits


def find_missing_good(text: str) -> list:
    missing = []
    for pattern, msg in GOOD_REQUIREMENTS:
        if not re.search(pattern, text, re.IGNORECASE):
            missing.append(msg)
    return missing


def main():
    if len(sys.argv) < 2:
        print("用法: validate.py <sample.md>", file=sys.stderr)
        sys.exit(EXIT_FILE_ERROR)

    sample_path = sys.argv[1]
    text = read_sample(sample_path)
    fname = Path(sample_path).name.lower()
    is_bad = "bad" in fname

    errors = []

    violations = find_violations(text)
    if is_bad:
        if not violations:
            errors.append("BAD 样例未命中任何已知违规模式（应至少命中一条）")
        else:
            errors.append(f"BAD 样例命中 {len(violations)} 条违规（预期失败）：{'; '.join(violations)}")
    else:
        if violations:
            errors.append(f"GOOD 样例命中违规（不应有）：{'; '.join(violations)}")
        missing = find_missing_good(text)
        errors.extend(missing)

    if errors:
        print(f"验证失败（{len(errors)} 项）：", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(EXIT_FAIL)

    print("验证通过")
    sys.exit(EXIT_OK)


if __name__ == "__main__":
    main()
