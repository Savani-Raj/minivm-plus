# MiniVM+ - Managed Runtime Compiler with Advanced Optimization Pipeline

A complete compiler and managed runtime implementation demonstrating modern compiler backend techniques, including multi-level optimizations, runtime profiling, and JIT compilation concepts.

## 🎯 Project Overview

This project implements a complete compiler pipeline for a simple language, featuring a sophisticated optimization system that demonstrates key compiler backend techniques required for modern managed runtimes (JVM, V8, etc.).

### 🔥 Key Achievements

- **45.5% instruction reduction** through advanced optimizations
- **Multi-level optimization pipeline**: Basic → Advanced → Feedback-directed
- **Runtime profiling system** for optimization guidance
- **JIT compilation concepts** and tiered compilation decisions
- **Complete bytecode VM** with execution engine

## 🏗️ Architecture

Source Code → Lexer → Parser → AST → IR Generator → Optimization Pipeline → Bytecode → VM
↓ ↑
Profiler → Feedback Optimizer → JIT Compiler

text

### Optimization Pipeline

1. **Basic Optimizations**: Constant folding, constant propagation, algebraic simplification
2. **Advanced Optimizations**: Strength reduction, copy propagation, common subexpression elimination
3. **Feedback-Directed**: Profile-guided optimizations based on runtime data

## 📊 Performance Highlights

| Example                | Original Instructions | Optimized Instructions | Reduction |
| ---------------------- | --------------------- | ---------------------- | --------- |
| Advanced Optimizations | 11                    | 6                      | 45.5%     |
| Fibonacci Demo         | 7                     | 4                      | 42.9%     |
| Simple Working         | 10                    | 8                      | 20%       |

### Advanced Optimization Examples

- **Strength Reduction**: `x * 2` → `x + x`, `x / 2` → `x >> 1`
- **Constant Folding**: `2 + 3` → `5`
- **Common Subexpression Elimination**: Duplicate computations removed
- **Dead Code Elimination**: Unused variables and instructions removed

## 🚀 Features

### ✅ Core Compiler

- **Lexer & Parser** with proper error handling
- **AST Generation** for expression trees
- **IR (Intermediate Representation)** with SSA-like properties
- **Multi-pass Optimizer** with sophisticated analysis

### ✅ Advanced Optimizations

- **Constant Propagation & Folding**
- **Algebraic Simplification** (`x + 0` → `x`, `x * 1` → `x`)
- **Strength Reduction** (expensive ops → cheaper equivalents)
- **Common Subexpression Elimination**
- **Dead Code Elimination** with dependency analysis
- **Copy Propagation**

### ✅ Runtime System

- **Bytecode Virtual Machine** with stack-based execution
- **Runtime Profiling** (type profiles, branch prediction, hot path detection)
- **Feedback-Directed Optimization** using profile data
- **Tiered Compilation** concepts (Interpreter → JIT → Optimized)
- **JIT Compilation Foundation** for dynamic compilation

## 📁 Project Structure

src/
├── compiler.py # Parser & IR generator
├── vm.py # Virtual machine with bytecode execution
├── ir_optimizer.py # Basic optimization passes
├── ir_optimizer_advanced.py # Advanced optimizations (strength reduction, etc.)
├── profiler.py # Runtime profiling system
├── feedback_optimizer.py # Profile-guided optimizations
├── jit_compiler.py # JIT compilation concepts
└── run.py # Main execution & demonstration

examples/
├── advanced.mvm # Demonstrates strength reduction & advanced opts
├── fib.mvm # Common subexpression elimination demo
├── simple_working.mvm # Basic optimization pipeline
└── working_functions.mvm # Complete working examples

text

## 🛠️ Quick Start

```bash
# See the complete optimization pipeline in action
python src/run.py examples/advanced.mvm

# Test common subexpression elimination
python src/run.py examples/fib.mvm

# View all optimization stages
python src/run.py examples/simple_working.mvm
🎓 Learning Outcomes
This project demonstrates deep understanding of:

Compiler Backend Architecture
Intermediate representation design

Data flow analysis frameworks

Optimization pass scheduling

Code generation techniques

Managed Runtime Concepts
Just-in-time (JIT) compilation principles

Profile-guided optimization (PGO)

Tiered compilation strategies

Bytecode interpreter design

Advanced Optimization Techniques
Strength reduction and peephole optimization

Constant propagation with copy analysis

Dead code elimination with use-def chains

Common subexpression elimination

🔬 Technical Implementation
Optimization Pipeline Details
The compiler implements a sophisticated multi-stage optimization pipeline:

Constant Folding: Evaluate constant expressions at compile time

Constant Propagation: Replace variables with known constant values

Algebraic Simplification: Apply mathematical identities

Strength Reduction: Replace expensive operations with cheaper equivalents

Common Subexpression Elimination: Remove redundant computations

Dead Code Elimination: Remove unused instructions

Copy Propagation: Eliminate redundant copy operations

Runtime Profiling System
Type Profiling: Track variable types for specialization

Branch Profiling: Collect branch prediction data

Hot Path Detection: Identify frequently executed code regions

Function Call Profiling: Track function invocation frequency

📈 Example Output
text
=== Optimization Analysis ===
Original instructions:      11
After basic optimizations:  9
After advanced optimizations: 6
After feedback optimization: 6
Total reduction:           5 instructions (45.5%)
🎥 Demo
bash
# Clone and explore
git clone https://github.com/Savani-Raj/minivm-plus.git
cd minivm-plus

# See the complete optimization pipeline
python src/run.py examples/advanced.mvm

# Output shows:
# - Original IR with 11 instructions
# - Basic optimized IR with constant folding
# - Advanced optimized IR with strength reduction
# - Final optimized IR with 6 instructions (45.5% reduction)
# - Generated bytecode and program execution
🤝 Contributing
This project was developed as a demonstration of compiler backend techniques for research and educational purposes.

📄 License
MIT License - See LICENSE file for details.
```
