# -*- coding: utf-8 -*-
"""
Данные авторского курса «LingvoDidactic PBL 1.0».

Цифровая образовательная система развития лингводидактических компетенций
будущих учителей русского языка на основе технологий проблемного обучения.

Каждый module0N.py содержит словарь MODULE со структурой:
    order, title, slug, short_description, description, level,
    duration_hours, xp_reward, lessons[], quiz{}
"""
from .module01 import MODULE as MODULE_01
from .module02 import MODULE as MODULE_02
from .module03 import MODULE as MODULE_03
from .module04 import MODULE as MODULE_04
from .module05 import MODULE as MODULE_05
from .module06 import MODULE as MODULE_06
from .module07 import MODULE as MODULE_07
from .module08 import MODULE as MODULE_08
from .module09 import MODULE as MODULE_09
from .module10 import MODULE as MODULE_10
from .diagnostic import DIAGNOSTIC_TESTS as _ENTRY_DIAGNOSTIC_TESTS
from .diagnostic_complex import DIAGNOSTIC_COMPLEX

MODULES = [
    MODULE_01, MODULE_02, MODULE_03, MODULE_04, MODULE_05,
    MODULE_06, MODULE_07, MODULE_08, MODULE_09, MODULE_10,
]

DIAGNOSTIC_TESTS = _ENTRY_DIAGNOSTIC_TESTS + [DIAGNOSTIC_COMPLEX]
