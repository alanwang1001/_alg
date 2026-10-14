#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lambda Calculus 解譯器（顯示完整 β 歸約過程）
============================================

兩種表示法：
  * 有名稱版本 (named)    ：變數用名字，代換時自動做 α 轉換避免變數捕獲
  * 無名稱版本 (nameless) ：De Bruijn 索引，λ.λ.1 0 這種寫法，完全不需要 α 轉換

兩種歸約策略：
  * normal      正規序（最左最外），只要有正規形就一定找得到
  * applicative 應用序（最左最內），可能在有正規形的項上無窮迴圈
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, replace
from typing import Optional, Union

# ════════════════════════════════════════════════════════════
#  1. 資料結構
# ════════════════════════════════════════════════════════════

# ---- 有名稱 ----
@dataclass(frozen=True)
class Var:
    name: str

@dataclass(frozen=True)
class Abs:
    param: str
    body: "Named"

@dataclass(frozen=True)
class App:
    fn: "Named"
    arg: "Named"

Named = Union[Var, Abs, App]

# ---- 無名稱 (De Bruijn) ----
@dataclass(frozen=True)
class DVar:          # 被綁定的變數：索引 0 表示最近的 λ
    idx: int

@dataclass(frozen=True)
class DFree:         # 自由變數保留名字
    name: str

@dataclass(frozen=True)
class DAbs:
    body: "Nameless"

@dataclass(frozen=True)
class DApp:
    fn: "Nameless"
    arg: "Nameless"

Nameless = Union[DVar, DFree, DAbs, DApp]

ABS_T = (Abs, DAbs)
APP_T = (App, DApp)

MARK_L, MARK_R = "【", "】"

# ════════════════════════════════════════════════════════════
#  2. 剖析器
# ════════════════════════════════════════════════════════════

class ParseError(Exception):
    pass

IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_']*")
TOKEN_RE = re.compile(r"\s*(λ|\\|\.|\(\vert{}\)|[A-Za-z_][A-Za-z0-9_']*|\d+)")
LAMBDAS = ("λ", "\\")

def tokenize(src: str) -> list[str]:
    tokens, pos, src = [], 0, src.rstrip()
    while pos < len(src):
        m = TOKEN_RE.match(src, pos)
        if not m:
            bad = src[pos:].lstrip()[:1]
            raise ParseError(f"無法辨識的字元：{bad!r}")
        tokens.append(m.group(1))
        pos = m.end()
    return tokens

def church(n: int) -> Named:
    body: Named = Var("x")
    for _ in range(n):
        body = App(Var("f"), body)
    return Abs("f", Abs("x", body))

class Parser:
    def __init__(self, tokens: list[str]):
        self.t, self.i = tokens, 0

    def peek(self) -> Optional[str]:
        return self.t[self.i] if self.i < len(self.t) else None

    def next(self) -> str:
        tok = self.peek()
        if tok is None:
            raise ParseError("運算式不完整，意外結束")
        self.i += 1
        return tok

    def parse(self) -> Named:
        term = self.term()
        if self.peek() is not None:
            raise ParseError(f"多餘的符號：{self.peek()!r}")
        return term

    def term(self) -> Named:
        return self.lam() if self.peek() in LAMBDAS else self.app()

    def lam(self) -> Named:
        self.next()  # 吃掉 λ
        params = []
        while self.peek() is not None and IDENT_RE.fullmatch(self.peek()):
            params.append(self.next())
        if not params:
            raise ParseError("λ 後面需要至少一個參數名稱")
        if self.next() != ".":
            raise ParseError("參數列後面需要 '.'")
        body = self.term()
        for p in reversed(params):
            body = Abs(p, body)
        return body

    def app(self) -> Named:
        items = [self.atom()]
        while True:
            tok = self.peek()
            if tok is None or tok == ")":
                break
            if tok in LAMBDAS:           # f λx.x  ：λ 一路延伸到最右邊
                items.append(self.lam())
                break
            items.append(self.atom())
        result = items[0]
        for it in items[1:]:
            result = App(result, it)
        return result

    def atom(self) -> Named:
        tok = self.next()
        if tok == "(":
            t = self.term()
            if self.next() != ")":
                raise ParseError("缺少右括號 ')'")
            return t
        if tok.isdigit():
            return church(int(tok))
        if IDENT_RE.fullmatch(tok):
            return Var(tok)
        raise ParseError(f"此處不該出現 {tok!r}")

def parse(src: str) -> Named:
    return Parser(tokenize(src)).parse()

# ════════════════════════════════════════════════════════════
#  3. 有名稱版本：自由變數、α 轉換、代換
# ════════════════════════════════════════════════════════════

def free_vars(t: Named) -> set[str]:
    if isinstance(t, Var):
        return {t.name}
    if isinstance(t, Abs):
        return free_vars(t.body) - {t.param}
    return free_vars(t.fn) | free_vars(t.arg)

def fresh(name: str, avoid: set[str]) -> str:
    cand = name + "'"
    while cand in avoid:
        cand += "'"
    return cand

def subst(t: Named, x: str, v: Named, notes: list[str]) -> Named:
    """t[x := v]，遇到變數捕獲時自動 α 轉換，並把動作記在 notes。"""
    if x not in free_vars(t):
        return t
    if isinstance(t, Var):                      # 此時 t.name == x
        return v
    if isinstance(t, App):
        return App(subst(t.fn, x, v, notes), subst(t.arg, x, v, notes))
    if t.param in free_vars(v):
        avoid = free_vars(v) | free_vars(t.body) | {x}
        new = fresh(t.param, avoid)
        notes.append(f"α 轉換：把內層的 {t.param} 改名為 {new}（避免捕獲自由變數 {t.param}）")
        body = subst(t.body, t.param, Var(new), [])
        return Abs(new, subst(body, x, v, notes))
    return Abs(t.param, subst(t.body, x, v, notes))

def expand(t: Named, env: dict[str, Named], bound: frozenset = frozenset()) -> Named:
    """把自由出現、且已被定義的名稱展開成它的定義。"""
    if isinstance(t, Var):
        return env[t.name] if (t.name not in bound and t.name in env) else t
    if isinstance(t, Abs):
        return Abs(t.param, expand(t.body, env, bound | {t.param}))
    return App(expand(t.fn, env, bound), expand(t.arg, env, bound))

def pp_named(t: Named, path: Optional[tuple] = None) -> str:
    if path == ():
        return MARK_L + pp_named(t) + MARK_R
    if isinstance(t, Var):
        return t.name
    if isinstance(t, Abs):
        params, b, p = [t.param], t.body, _down(path, "body")
        while isinstance(b, Abs) and p != ():   # λx.λy.M 合併寫成 λx y.M
            params.append(b.param)
            p, b = _down(p, "body"), b.body
        return "λ" + " ".join(params) + "." + pp_named(b, p)
    f = pp_named(t.fn, _down(path, "fn"))
    a = pp_named(t.arg, _down(path, "arg"))
    if isinstance(t.fn, Abs):
        f = f"({f})"
    if isinstance(t.arg, (Abs, App)):
        a = f"({a})"
    return f"{f} {a}"

def _down(path: Optional[tuple], head: str) -> Optional[tuple]:
    return path[1:] if path and path[0] == head else None

# ════════════════════════════════════════════════════════════
#  4. 無名稱版本：De Bruijn 轉換、shift、代換
# ════════════════════════════════════════════════════════════

def to_nameless(t: Named, ctx: tuple = ()) -> Nameless:
    if isinstance(t, Var):
        rev = ctx[::-1]
        return DVar(rev.index(t.name)) if t.name in rev else DFree(t.name)
    if isinstance(t, Abs):
        return DAbs(to_nameless(t.body, ctx + (t.param,)))
    return DApp(to_nameless(t.fn, ctx), to_nameless(t.arg, ctx))

def shift(t: Nameless, d: int, cutoff: int = 0) -> Nameless:
    """把 t 中『自由』的索引（>= cutoff）加上 d。"""
    if isinstance(t, DVar):
        return DVar(t.idx + d) if t.idx >= cutoff else t
    if isinstance(t, DFree):
        return t
    if isinstance(t, DAbs):
        return DAbs(shift(t.body, d, cutoff + 1))
    return DApp(shift(t.fn, d, cutoff), shift(t.arg, d, cutoff))

def dsubst(t: Nameless, j: int, s: Nameless) -> Nameless:
    """t[j := s]"""
    if isinstance(t, DVar):
        return s if t.idx == j else t
    if isinstance(t, DFree):
        return t
    if isinstance(t, DAbs):
        return DAbs(dsubst(t.body, j + 1, shift(s, 1)))
    return DApp(dsubst(t.fn, j, s), dsubst(t.arg, j, s))

def pp_nameless(t: Nameless, path: Optional[tuple] = None) -> str:
    if path == ():
        return MARK_L + pp_nameless(t) + MARK_R
    if isinstance(t, DVar):
        return str(t.idx)
    if isinstance(t, DFree):
        return t.name
    if isinstance(t, DAbs):
        return "λ." + pp_nameless(t.body, _down(path, "body"))
    f = pp_nameless(t.fn, _down(path, "fn"))
    a = pp_nameless(t.arg, _down(path, "arg"))
    if isinstance(t.fn, DAbs):
        f = f"({f})"
    if isinstance(t.arg, (DAbs, DApp)):
        a = f"({a})"
    return f"{f} {a}"

# ════════════════════════════════════════════════════════════
#  5. 兩種版本共用的歸約引擎
# ════════════════════════════════════════════════════════════

def find_redex(t, strategy: str) -> Optional[tuple]:
    """回傳下一個要歸約的 redex 的路徑"""
    if isinstance(t, APP_T):
        if strategy == "normal" and isinstance(t.fn, ABS_T):
            return ()
        p = find_redex(t.fn, strategy)
        if p is not None:
            return ("fn",) + p
        p = find_redex(t.arg, strategy)
        if p is not None:
            return ("arg",) + p
        if isinstance(t.fn, ABS_T):             # 應用序：子項都化簡完才輪到自己
            return ()
        return None
    if isinstance(t, ABS_T):
        p = find_redex(t.body, strategy)
        return None if p is None else ("body",) + p
    return None

def get_at(t, path):
    for h in path:
        t = getattr(t, h)
    return t

def reduce_at(t, path, beta):
    if not path:
        return beta(t)
    h = path[0]
    return replace(t, **{h: reduce_at(getattr(t, h), path[1:], beta)})

def short(s: str, n: int = 70) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"

class NamedCalc:
    title = "有名稱版本 (named)"
    pp = staticmethod(pp_named)

    @staticmethod
    def beta(redex: App, notes: list[str]):
        return subst(redex.fn.body, redex.fn.param, redex.arg, notes)

    @staticmethod
    def describe(redex: App) -> str:
        return (f"β 歸約：把 λ{redex.fn.param} 的本體中所有 {redex.fn.param} "
                f"代換成 {short(pp_named(redex.arg))}")

class NamelessCalc:
    title = "無名稱版本 (De Bruijn)"
    pp = staticmethod(pp_nameless)

    @staticmethod
    def beta(redex: DApp, notes: list[str]):
        body, arg = redex.fn.body, redex.arg
        return shift(dsubst(body, 0, shift(arg, 1)), -1)

    @staticmethod
    def describe(redex: DApp) -> str:
        return (f"β 歸約：本體中的索引 0 代換成 {short(pp_nameless(redex.arg))}"
                f"（參數先 shift +1 以通過 λ，代換後整體 shift −1）")

STRATEGY_NAME = {"normal": "正規序 normal order（最左最外）",
                 "applicative": "應用序 applicative order（最左最內）"}

def trace(calc, term, strategy: str, max_steps: int):
    print(f"\n  ── {calc.title}｜{STRATEGY_NAME[strategy]} ──")
    t, steps = term, 0
    while True:
        path = find_redex(t, strategy)
        if path is None:
            print(f"  {steps:>3}  {calc.pp(t)}   ✔ 正規形")
            return t, steps, True
        if steps >= max_steps:
            print(f"  {steps:>3}  {calc.pp(t)}")
            print(f"       ⚠ 已達步數上限 {max_steps}，停止（此項可能不會終止）")
            return t, steps, False
        print(f"  {steps:>3}  {calc.pp(t, path)}")
        notes: list[str] = []
        redex = get_at(t, path)
        print(f"       └ {calc.describe(redex)}")
        t = reduce_at(t, path, lambda r: calc.beta(r, notes))
        for n in notes:
            print(f"       └ {n}")
        steps += 1

# ════════════════════════════════════════════════════════════
#  6. 結果辨識（Church 數字 / 布林）
# ════════════════════════════════════════════════════════════

def describe_value(t: Nameless) -> Optional[str]:
    if isinstance(t, DAbs) and isinstance(t.body, DAbs):
        b, n = t.body.body, 0
        while isinstance(b, DApp) and b.fn == DVar(1):
            n, b = n + 1, b.arg
        if b == DVar(0):
            return f"Church 數字 {n}" + ("（同時也是 FALSE）" if n == 0 else "")
        if t.body.body == DVar(1):
            return "TRUE（λx y.x）"
    return None

# ════════════════════════════════════════════════════════════
#  7. 內建函式庫與範例程式
# ════════════════════════════════════════════════════════════

PRELUDE = """
ID     = λx.x
TRUE   = λx y.x
FALSE  = λx y.y
AND    = λp q.p q p
OR     = λp q.p p q
NOT    = λp.p FALSE TRUE
IF     = λp a b.p a b
SUCC   = λn f x.f (n f x)
ADD    = λm n f x.m f (n f x)
MUL    = λm n f.m (n f)
POW    = λb e.e b
ISZERO = λn.n (λx.FALSE) TRUE
PAIR   = λx y f.f x y
FST    = λp.p TRUE
SND    = λp.p FALSE
PRED   = λn f x.n (λg h.h (g f)) (λu.x) (λu.u)
SUB    = λm n.n PRED m
Y      = λf.(λx.f (x x)) (λx.f (x x))
OMEGA  = (λx.x x) (λx.x x)
"""

EXAMPLES = [
    ("變數捕獲 → 觸發 α 轉換",         "(λx.λy.x y) y",            None, None),
    ("布林：AND TRUE FALSE",           "AND TRUE FALSE",          None, None),
    ("Church 加法：ADD 2 3",           "ADD 2 3",                 None, None),
    ("正規序：(λx.y) OMEGA 可以終止",    "(λx.y) OMEGA",            "normal", 20),
    ("應用序：同一個項卻無窮迴圈",        "(λx.y) OMEGA",            "applicative", 5),
]

# ════════════════════════════════════════════════════════════
#  8. 執行程式 / REPL
# ════════════════════════════════════════════════════════════

DEF_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_']*)\s*=\s*(.+)")

def new_env() -> dict[str, Named]:
    env: dict[str, Named] = {}
    for line in PRELUDE.strip().splitlines():
        define(line, env, verbose=False)
    return env

def define(line: str, env: dict, verbose: bool = True) -> bool:
    m = DEF_RE.fullmatch(line.strip())
    if not m:
        return False
    name, rhs = m.groups()
    env[name] = expand(parse(rhs), env)
    if verbose:
        print(f"定義 {name} = {short(pp_named(env[name]), 90)}")
    return True

def evaluate(src: str, env: dict, mode: str, strategy: str, max_steps: int, title: str = ""):
    print("\n" + "═" * 72)
    if title:
        print(f"【{title}】")
    print(f"輸入：{src}")
    term = expand(parse(src), env)
    print(f"展開：{pp_named(term)}")
    results = {}
    if mode in ("named", "both"):
        results["named"] = trace(NamedCalc, term, strategy, max_steps)
    if mode in ("nameless", "both"):
        dterm = to_nameless(term)
        print(f"\n  （轉成 De Bruijn 索引：{pp_nameless(dterm)}）")
        results["nameless"] = trace(NamelessCalc, dterm, strategy, max_steps)

    print()
    for key, (final, steps, ok) in results.items():
        label = "有名稱" if key == "named" else "無名稱"
        shown = pp_named(final) if key == "named" else pp_nameless(final)
        print(f"  結果［{label}］：{shown}   （{steps} 次 β 歸約{'' if ok else '，未到正規形'}）")
    
    if mode == "both" and all(ok for *_, ok in results.values()):
        same = to_nameless(results["named"][0]) == results["nameless"][0]
        print(f"  兩種版本的結果{'一致 ✔（α 等價）' if same else '不一致 ✘'}")

def run_program(text: str, env: dict, mode: str, strategy: str, max_steps: int):
    for raw in text.splitlines():
        line = raw.split("#")[0].strip()
        if not line: continue
