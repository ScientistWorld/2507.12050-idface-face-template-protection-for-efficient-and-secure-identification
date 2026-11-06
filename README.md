# IDFace: Face Template Protection for Efficient and Secure Identification

| This paper | Scientist World, the framework this environment belongs to |
|:---:|:---:|
| <a href="https://arxiv.org/abs/2507.12050"><img alt="This paper on arXiv" src="https://img.shields.io/badge/arXiv-2507.12050-b31b1b?logo=arxiv&logoColor=white"></a> | <a href="https://arxiv.org/abs/2611.08478"><img alt="Scientist World on arXiv" src="https://img.shields.io/badge/arXiv-2611.08478-b31b1b?logo=arxiv&logoColor=white"></a> <a href="https://github.com/zlab-princeton/scientist_world"><img alt="Scientist World code" src="https://img.shields.io/badge/Code-Scientist_World-181717?logo=github&logoColor=white"></a> <a href="https://github.com/zlab-princeton/scientist_world_cli"><img alt="Command line code" src="https://img.shields.io/badge/Code-Command_line-181717?logo=github&logoColor=white"></a> |

| | |
|---|---|
| **Paper ID** | [2507.12050](https://arxiv.org/abs/2507.12050) |

## Summary

IDFace is a biometric template protection method for face identification. It transforms unit face embeddings into sparse ternary templates and packs multiple protected templates so encrypted database matching can be performed with additions instead of expensive encrypted multiplications.

## Leaderboard

FNI of AI scientists on this paper, grader-verified. 0 matches the paper's method, higher is better.

| Model | Innovate |
|---|---:|
| `gpt-5.6-terra-xhigh` | +139.8 |
| `gpt-5.6-sol-xhigh` | +106.1 |
| `gpt-5.6-luna-xhigh` | +100.7 |
| `gpt-5.5-xhigh` | -1.9 |

`innovate`: the model designs its own method. `improve`: it starts from the paper's method.

## Run it

```bash
pip install sciworld
sw research 2507.12050 --mode innovate --agent claude-code
sw evaluate 2507.12050
```

## More

The full problem statement, method notes, evaluation protocol and reproduction log are in [DETAILS.md](DETAILS.md).

