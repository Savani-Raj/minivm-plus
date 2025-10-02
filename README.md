markdown

# MiniVM+ - Managed Runtime Compiler with Profiling & JIT

[![Run Tests](https://github.com/yourusername/minivm-plus/actions/workflows/test.yml/badge.svg)](https://github.com/yourusername/minivm-plus/actions/workflows/test.yml)

A complete compiler and managed runtime implementation demonstrating modern compiler backend techniques, including profiling, feedback-directed optimization, and JIT compilation concepts.

## 🎯 Project Overview

This project implements a complete compiler pipeline for a simple language, featuring:

- **Lexer & Parser** - Source code to AST
- **IR Generation** - Intermediate representation with optimizations
- **Multi-level Optimizations** - Basic to advanced optimization passes
- **Runtime Profiling** - Type profiling, branch prediction, hot path detection
- **Feedback-Directed Optimization** - Profile-guided optimizations
- **Tiered Compilation** - Interpreter → Baseline JIT → Optimizing JIT
- **Virtual Machine** - Bytecode execution engine

## 🆕 Latest Updates

### Advanced Optimization System

- **Strength Reduction**: `x * 2` → `x + x`, `x / 2` → `x >> 1`
- **Copy Propagation**: Eliminate redundant move operations
- **Control Flow Analysis**: Basic block construction and optimization
- **Enhanced Dead Code Elimination**: Dependency-aware code removal

### Runtime Profiling Infrastructure

- **Type Profiling**: Track variable types for JIT specialization
- **Branch Prediction**: Profile branch behavior for optimization
- **Hot Path Detection**: Identify frequently executed code regions
- **Profile Reports**: Generate optimization suggestions

### Feedback-Directed Compilation

- **Profile-Guided Optimizations**: Use runtime data to drive optimizations
- **Tiered Compilation**: Multi-level optimization strategy
- **JIT Compilation Foundation**: Dynamic compilation skeleton

## 📊 Optimization Performance

**Example: Advanced Optimization Demo**
Original: 11 instructions → Optimized: 5 instructions (54.5% reduction)

text

## 🏗️ Architecture

Source → Tokenizer → Parser → AST → IR Generator → Optimizer → VM
↑ ↓
Profiler → Feedback Optimizer
↓ ↓
Tiered Compiler → JIT Compiler

text

## 📁 Updated Project Structure

src/
├── compiler.py # Parser & IR generator
├── vm.py # Virtual machine
├── ir_optimizer.py # Basic optimizations
├── ir_optimizer_advanced.py # Advanced optimizations (NEW)
├── profiler.py # Runtime profiling (NEW)
├── feedback_optimizer.py # Profile-guided optimizations (NEW)
├── jit_compiler.py # JIT compilation concepts (NEW)
└── run.py # Main execution

examples/
├── fib.mvm # Fibonacci demo
└── advanced.mvm # Optimization demo (NEW)

text

## 🚀 Quick Start

```bash
# Run with full optimization pipeline
python src/run.py examples/advanced.mvm

# See optimization progress and profiling
python src/run.py examples/fib.mvm
🎓 Learning Outcomes
This project demonstrates understanding of:

Modern compiler backend architecture

Managed runtime concepts (JVM, V8, etc.)

Profile-guided optimization (PGO)

Just-in-time (JIT) compilation

Dynamic language implementation

🔄 Recent Improvements
Advanced optimization passes

Runtime profiling system

Feedback-directed optimization

Tiered compilation concepts

Function support with control flow

Full JIT compilation implementation

📈 Example Output
text
=== Runtime Profile Report ===
Type Profiles:
  a: int (count: 3)
Hot Blocks:
  main: 1501 executions
Optimization Suggestions:
  - Hot path optimization for 1 blocks
  - - Inline candidates identified: ['factorial']

MIT License - see [LICENSE](LICENSE) file for details.
```
