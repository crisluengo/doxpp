# libclang Python Bindings

This is a copy of the Python bindings for libclang taken from
here: https://github.com/llvm/llvm-project/tree/master/clang/bindings/python/clang

The copy was made from master on 2020-10-22, when that directory was
at revision [ccc43e3](https://github.com/llvm/llvm-project/commit/ccc43e337cfa62b4787c39aefd3559ed39f78556).

Changes applied to the code to allow running the copy:
1. `cindex.py`, line 68, replace `import clang.enumerations` with `from . import enumerations`.
2. `cindex.py`, line 4191, replace `clang.enumerations.TokenKinds` with `enumerations.TokenKinds`.
